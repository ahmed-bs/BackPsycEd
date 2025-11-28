-- PostgreSQL SQL migration for adding isPeu and done fields to profile_item table
-- Run this SQL if you're using PostgreSQL database

-- Add isPeu boolean field with default value false
ALTER TABLE profile_item 
ADD COLUMN "isPeu" BOOLEAN NOT NULL DEFAULT FALSE;

-- Add done boolean field with default value false
ALTER TABLE profile_item 
ADD COLUMN "done" BOOLEAN NOT NULL DEFAULT FALSE;

-- Optional: Add comments to the columns for documentation
COMMENT ON COLUMN profile_item."isPeu" IS 'Boolean field indicating if the item is peu';
COMMENT ON COLUMN profile_item."done" IS 'Boolean field indicating if the item is done';exi

