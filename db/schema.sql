CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TABLE IF NOT EXISTS civic_subscriptions (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 email text NOT NULL UNIQUE CHECK (length(email) BETWEEN 4 AND 250),
 zip char(5) NOT NULL CHECK (zip ~ '^[0-9]{5}$'),
 topics text[] NOT NULL,
 verify_hash char(64),
 unsub_hash char(64),
 status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','active','unsubscribed')),
 created_at timestamptz NOT NULL DEFAULT now(),
 verified_at timestamptz,
 expires_at timestamptz,
 last_notified_at timestamptz
);
CREATE INDEX IF NOT EXISTS civic_subscriptions_status_idx ON civic_subscriptions(status);
CREATE UNIQUE INDEX IF NOT EXISTS civic_subscriptions_unsub_hash_idx ON civic_subscriptions(unsub_hash) WHERE unsub_hash IS NOT NULL;
CREATE TABLE IF NOT EXISTS civic_deliveries (
 subscription_id uuid NOT NULL REFERENCES civic_subscriptions(id) ON DELETE CASCADE,
 policy_id text NOT NULL,
 sent_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(subscription_id,policy_id)
);
