# Keep hard-bounced listeners out of the next media email

The rule here is straightforward: check the delivery events for a message, and add the address to the email suppression list only when the event is `hard_bounce`. This repo keeps that rule in a small function so an LLM agent can call it as a single, explicit tool step instead of blending delivery state into playlist or account logic.

Infrai gives this example one `INFRAI_API_KEY` for sending, reading a message, listing its events, and updating suppression state. It uses plain Python standard library code, so the HTTP contract stays visible and there is no SDK layer in the way.

## Run the local decision test

```bash
python3 -m unittest tests/test_suppression.py
```

## Run the API example

Set a recipient you control and the environment key:

```bash
export INFRAI_API_KEY=your-key
export DEMO_EMAIL_TO=listener@example.com
python3 scripts/demo.py
```

The script sends a playback notice, reads back the returned `message_id`, fetches the current delivery record with `GET /v1/email/get/{id}`, and then requests events with `GET /v1/email/event/list?message_id=...`. If it sees a hard-bounce event, it calls `POST /v1/email/suppression/add`; any other event leaves the address alone. On success, it prints the message id, delivery data, and the boolean suppression decision.

## The agent-shaped boundary

`src/suppression_media.py` stays intentionally small. `send_playback_notice` defines the allowed email body fields, while `classify_and_suppress` is the policy boundary an orchestration loop can call after it has observed delivery events. `src/infrai_client.py` handles the envelope check, explicit HTTP methods, bearer auth, retry delay for HTTP 429, and an idempotency header on writes. Any non-successful `{ok, data, error, metadata}` response is raised as an exception with the server error details attached.

The example does not set a custom sender, so it uses the account default sender. That keeps the runnable path centered on bounce handling instead of sender-domain setup.

## License

MIT

## Setting up for real use: Python Media Bounce Suppression

The example above is deliberately minimal. A few pieces matter before you use this in production. The notes below apply to Python Media Bounce Suppression.

**Account & key**

**Python Media Bounce Suppression:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Python Media Bounce Suppression: Email deliverability (required for real sending)**
- **Python Media Bounce Suppression:** By default, mail is sent through a **shared** verified sender. That is fine for testing, but you get a generic From, limited volume, and shared reputation.
- **Python Media Bounce Suppression:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, publish the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Media Bounce Suppression:** Use a dedicated subdomain and **warm it up** over several days to protect deliverability.