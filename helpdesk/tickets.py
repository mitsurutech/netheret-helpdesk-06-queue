"""Support requests (tickets): raising them, the queue and the detail page."""
from flask import Blueprint, abort, g, redirect, render_template, request, url_for
from sqlalchemy import case

from .auth import login_required, role_required
from .extensions import db
from .models import CATEGORIES, PRIORITIES, STAFF_ROLES, STATUSES, TIERS, Company, Ticket, User

bp = Blueprint("tickets", __name__)


def check_request_form(form, needs_company):
    """Check what was typed into the request form.

    Returns a dictionary of {field name: error message}. An empty dictionary
    means there were no problems.
    """
    errors = {}
    title = form.get("title", "").strip()
    if not title:
        errors["title"] = "Enter a short title for the problem."
    elif len(title) > 150:
        errors["title"] = "The title must be 150 characters or fewer."
    if not form.get("description", "").strip():
        errors["description"] = "Describe the problem."
    # Choices must be on the allowed list, even though the form only offers
    # those: somebody could send any value without using our form.
    if form.get("category") not in CATEGORIES:
        errors["category"] = "Choose a category."
    if form.get("priority") not in PRIORITIES:
        errors["priority"] = "Choose a priority."
    if needs_company:
        company_id = form.get("company_id", "")
        if not company_id.isdigit() or db.session.get(Company, int(company_id)) is None:
            errors["company_id"] = "Choose the customer's company."
    return errors


@bp.route("/requests/new", methods=["GET", "POST"])
@role_required("customer", "tier1", "manager")
def new_request():
    # Customers raise requests for their own company. Staff taking a phone
    # call raise them for a customer, so they choose the company.
    is_customer = g.user.role == "customer"
    errors = {}
    form = request.form
    if request.method == "POST":
        errors = check_request_form(form, needs_company=not is_customer)
        if not errors:
            ticket = Ticket(
                title=form["title"].strip(),
                description=form["description"].strip(),
                category=form["category"],
                priority=form["priority"],
                status="new",
                tier=1,
                company_id=g.user.company_id if is_customer else int(form["company_id"]),
                raised_by=g.user,
            )
            db.session.add(ticket)
            db.session.flush()  # gives the ticket its id
            ticket.set_reference()
            db.session.commit()
            return redirect(url_for("tickets.raised", ticket_id=ticket.id))

    companies = [] if is_customer else db.session.scalars(db.select(Company).order_by(Company.name)).all()
    return render_template(
        "tickets/new.html", form=form, errors=errors, companies=companies,
        categories=CATEGORIES, priorities=PRIORITIES,
    )


@bp.route("/requests/<int:ticket_id>/raised")
@login_required
def raised(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    # A customer may only see their own company's requests. We answer 404
    # (not found) so they cannot even tell that the request exists.
    if g.user.role == "customer" and ticket.company_id != g.user.company_id:
        abort(404)
    return render_template("tickets/raised.html", ticket=ticket)


@bp.route("/queue")
@role_required(*STAFF_ROLES)
def queue():
    """The list of requests, with filters chosen from the form at the top.

    The filters are in the address (a GET form), so a filtered queue can be
    bookmarked or shared.
    """
    status = request.args.get("status", "active")
    priority = request.args.get("priority", "")
    tier = request.args.get("tier", "")
    assigned = request.args.get("assigned", "")

    query = db.select(Ticket)
    # Each filter adds one more WHERE condition to the query.
    if status == "active":
        query = query.where(Ticket.status.in_(["new", "open", "waiting"]))
    elif status in STATUSES:
        query = query.where(Ticket.status == status)
    if priority in PRIORITIES:
        query = query.where(Ticket.priority == priority)
    if tier.isdigit() and int(tier) in TIERS:
        query = query.where(Ticket.tier == int(tier))
    if assigned == "me":
        query = query.where(Ticket.assigned_to_id == g.user.id)
    elif assigned == "none":
        query = query.where(Ticket.assigned_to_id.is_(None))
    elif assigned.isdigit():
        query = query.where(Ticket.assigned_to_id == int(assigned))

    # Most urgent first: CASE turns each priority into a number to sort by.
    urgency = case({"critical": 0, "high": 1, "medium": 2, "low": 3}, value=Ticket.priority)
    query = query.order_by(urgency, Ticket.created_at)
    tickets = db.session.scalars(query).all()

    staff = db.session.scalars(
        db.select(User).where(User.role.in_(STAFF_ROLES)).order_by(User.name)
    ).all()
    return render_template(
        "tickets/queue.html", tickets=tickets, staff=staff,
        statuses=STATUSES, priorities=PRIORITIES, tiers=TIERS,
        chosen={"status": status, "priority": priority, "tier": tier, "assigned": assigned},
    )


@bp.route("/requests/<int:ticket_id>")
@role_required(*STAFF_ROLES)
def detail(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    return render_template("tickets/detail.html", ticket=ticket)
