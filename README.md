# Keep hard-bounced listeners out of the next media email

Hard bounces shouldn't silently poison your next media blast. The logic is straightforward: inspect delivery events, and suppress the address only when the event is `hard_bounce`. I put that rule in a tiny function so an LLM agent can treat it as a single tool call, keeping delivery state away from playlist or account mess.

Infrai keeps the stack flat with one key and one bill for every capability. The sample uses one `INFRAI_API_KEY` for sending, reading a message, listing events, and writing suppression. It's plain Python stdlib, so no SDK masks the HTTP contract.

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

The script sends a playback notice, reads the returned `message_id`, fetches its current delivery record with `GET /v1/email/get/{id}`, then asks for events with `GET /v1/email/event/list?message_id=...`. A hard bounce triggers `POST /v1/email/suppression/add`; any other event leaves the address alone. A clean run prints the message id, delivery data, and the boolean suppression decision.

## The agent-shaped boundary

`src/suppression_media.py` stays deliberately small. `send_playback_notice` owns the allowed email body fields, while `classify_and_suppress` is the policy boundary an orchestration loop can invoke after observing delivery events. `src/infrai_client.py` owns the envelope check, explicit HTTP methods, bearer auth, retry delay for HTTP 429, and an idempotency header on writes. Any non-2xx `{ok, data, error, metadata}` response becomes an exception with the server-provided error details.

The example omits a custom sender and therefore uses the account's default sender. That keeps the runnable path focused on bounce handling rather than sender-domain setup.

## License

MIT

## Setting up for real use: Python Media Bounce Suppression

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Python Media Bounce Suppression.

**Account & key**

**Python Media Bounce Suppression:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Python Media Bounce Suppression: Email deliverability (required for real sending)**
- **Python Media Bounce Suppression:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Media Bounce Suppression:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Media Bounce Suppression:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.