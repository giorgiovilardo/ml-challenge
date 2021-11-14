# Journal of the challenge

## The name

Every good project must start with a name: the challenge kinda reminds me of a scraper,
so it's only natural that the name must be `scrapapelada`, an extremely funny pun.

No seriously, it's called `scrapapelada`. I'm not kidding, we all know
the quote about `naming is hard` so let's be done with it and never mention it again.

## Analysis of the business requirements

The most uncertain thing around the business requirements is the usage pattern;
is it a synchronous or an asynchronous service? A synchronous service, with aggressive timeouts
on the HTTP client, could be used in a SPA setting, maybe for some sort of widget or as an
alert service.

But the regex requirement kinda points towards an asynchronous service, as we
are not only network-bound but also cpu-bound on time-to-response fulfillment,
as matching a regex can potentially be time consuming and must happen serially
after retrieving the whole body ~ which might be in the order of gigabytes.

The second most uncertain thing is if there is a 1:1 mapping between a request
and the execution of a check, or if a request needs to start an infinite series of checks.

There is no mention of timings, intervals and whatnot, so I think it's
correct to think that one request equals one check.

### The async idea 

The system is going to accept, via POST body, an object of this kind:

```json
{
  "url": "a proper url, with schema, mandatory",
  "regex": "a regex in string format, optional"
}
```

The endpoint will take the data, generate a UUID, and put them in a task queue,
answering the response with this object, with a status code of `202 ACCEPTED`:

```json
{
  "message": "OK",
  "uuid": "an UUID"
}
```

After the item has gone to the queue, it will get processed there, by
the task runner. How to access the processing results? You don't,
no one asked to view the result via API. Maybe it will be looked at
directly inside the db. In any case we're returning an UUID for a reason :)

We can even take the asynchronicity to the extreme by actually not matching anything
to the regex unless someone wants to view it. Lazy evaluation all the things.

But...

### The synchronous reality

But the truth is no one really asked to make it async, and YAGNI is real enough
to avoid getting into the snakepits of the async implementation, which basically
needs a ton more pieces of software, complicates testing...and forces the client to
do a second request to see the results, which he might not want to do.

So while async would have been cool we'll stay async.

The service will accept the same request object:

```json
{
  "url": "a proper url, with schema, mandatory",
  "regex": "a regex in string format, optional"
}
```

but will output something like

```json
{
  "uuid": "an UUID",
  "url": "the requested url",
  "regex": "the requested regex, optional",
  "has_failed": bool,
  "status_code": int,
  "roundtrip": timedelta,
  "has_matched": bool
}
```

The last three fields and `regex` might not be present in the response as I prefer
to avoid nulls whenever possible and I esplicitly save if the request failed or not
rather than have some in-band failure values e.g. status code 0 or null.

The UUID is there as I like to attach an UUID to resources and tend to hide the `id` PK, to avoid enumeration
and in general to have some other reference other than the id.

We'll also save in the db the classic timestamps for creation/modification, but won't serialize them
back.

## Technical choices, v1

I'm rusty with Python and its ecosystem, I'm time constrained and I
absolutely don't want to deal with alembic, sqlalchemy, test infrastructure,
and so on, so a leaner framework a la FastAPI or Flask is out of the question.

Django + DRF looks like a sane choice to do it quickly enough.
I think I'll use Marshmallow for validation insted of DRF stuff which I honestly found
bizantine and needlessly complex. Requests is my http client of choice.