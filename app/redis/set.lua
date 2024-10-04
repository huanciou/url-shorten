-- set.lua

-- Function to set a value in Redis
local function set_value(key, value)
  redis.call('SET', key, value)
  return 'OK'
end

-- Function to get a value from Redis
local function get_value(key)
  local value = redis.call('GET', key)
  if value then
      return value
  else
      return nil  -- Return nil if the key does not exist
  end
end

-- Main logic to determine which function to call based on the operation
if ARGV[1] == 'set' then
  return set_value(ARGV[2], ARGV[3])  -- Call set_value with key and value
elseif ARGV[1] == 'get' then
  return get_value(ARGV[2])  -- Call get_value with key
else
  return 'Invalid operation'  -- Handle invalid operations
end
