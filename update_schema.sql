-- Add shared_itineraries table for temporary sharing functionality
CREATE TABLE IF NOT EXISTS shared_itineraries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    share_id VARCHAR(50) UNIQUE NOT NULL,
    data JSONB NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_shared_itineraries_share_id ON shared_itineraries(share_id);
CREATE INDEX IF NOT EXISTS idx_shared_itineraries_expires_at ON shared_itineraries(expires_at);

-- Optional: Add a function to clean up expired shared itineraries
CREATE OR REPLACE FUNCTION cleanup_expired_shared_itineraries()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM shared_itineraries WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- You can manually run this to clean up expired shares:
-- SELECT cleanup_expired_shared_itineraries();