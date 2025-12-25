-- Add user_preferences table for user profile settings
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    preferences JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create or replace the trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add a trigger to update 'updated_at' for user_preferences
DROP TRIGGER IF EXISTS set_user_preferences_timestamp ON user_preferences;
CREATE TRIGGER set_user_preferences_timestamp
BEFORE UPDATE ON user_preferences
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

-- Verify the table was created
SELECT 'user_preferences table created successfully!' AS status;
