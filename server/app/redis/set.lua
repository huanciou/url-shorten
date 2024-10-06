-- set.lua

local function set_value(key, value)
  redis.call('SET', key, value)
  return 'OK'
end

local function get_value(key)
  local value = redis.call('GET', key)
  if value then
      return value
  else
      return nil  
  end
end


if ARGV[1] == 'set' then
  return set_value(ARGV[2], ARGV[3])  
elseif ARGV[1] == 'get' then
  return get_value(ARGV[2]) 
else
  return 'Invalid operation' 
end
