# Netheret help desk, step 06: queue and detail

A teaching example. Over sixteen steps we build a help desk web app for
Netheret, a made-up company that supports the IT of small businesses. This
step gives the help desk staff a queue of requests they can filter, and a
page showing everything about one request.

## What this step adds

- `/queue` in `helpdesk/tickets.py`: every request still to do, most urgent
  first, with filters for status, priority, tier and who it is assigned to.
- `/requests/<id>`: the detail page for one request.
- `helpdesk/filters.py`: template filters that show dates nicely.
- Coloured badges for priority and status, always with the word as well.
- Quick links on each staff dashboard, which are just queue filters.

## Run it

```
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
python seed.py
flask --app helpdesk run --debug
```

Sign in as `tier1@netheret.example` or `manager@netheret.example` (demo
password `password123`) and open Queue. Customers get "403 Forbidden" there.

## What to look at

- The filter form uses `method="get"`, so the filters end up in the
  address, for example `/queue?priority=critical&status=all`.
- `queue()` builds one query, adding a `where` for each filter chosen, and
  ignores any value that is not on its allowed list.
- `case(...)` sorts by urgency inside the SQL query: critical, high, medium,
  then low.
- Tables have a `caption` and `scope="col"` headers for screen readers.

## Learn this step

This is step 6 of 16 of **Task 2. Developing the solution**, a free series of T Level Digital Software Development
lessons that builds the Netheret help desk in agile sprints with Python and Flask. Read the lesson for this step:
[The request queue and filters](https://mitsurutech.co.uk/resources/t-level/dsd-t2-06-queue).

- Previous step: [step 05, raising a support request](https://github.com/mitsurutech/netheret-helpdesk-05-raise-request)
- Next step: [step 07, assigning, escalating and the timeline](https://github.com/mitsurutech/netheret-helpdesk-07-timeline)
- [Every free T Level Digital lesson](https://mitsurutech.co.uk/resources/t-level)
- [Teach these lessons to your class on MitsuruTech](https://mitsurutech.co.uk/learning), [see the pricing](https://mitsurutech.co.uk/pricing) or
  [start a free year for your college](https://mitsurutech.co.uk/signup)

## About

Written by [Mitsuru Technologies](https://mitsurutech.co.uk) (MitsuruTech) as a teaching example for T Level Digital
Software Development. The Netheret IT Support Solutions brief is from Pearson's sample assessment material; this code
and its notes are our own, and are not published, endorsed or approved by Pearson or the Department for Education.
'T Level' is a registered trade mark of the Department for Education.

