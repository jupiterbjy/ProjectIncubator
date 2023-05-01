low_watermark = 10
high_watermark = 90
check_interval = 2

redstone_emit_level = 15
redstone_off_level = 0     -- in case if you want throttling, not shutdown.
redstone_location = "top"

cell_location = "back"
cell_ident = "energy_cube"

monitor_ident = "monitor"
-- TODO: add auto detection

redstone.setOutput(redstone_location, false)


local function clear()
    term.clear()
    term.setCursorPos(1,1)
end


local function list_table(t)
    for key, val in pairs(t) do
        print(t[key])
    end
end


local function fetch_reference(target, skip_error)
    attached_table = peripheral.getNames()
    -- print("Connection list:")
    -- list_table(attached_table)
    -- print()
    
    for key, val in pairs(attached_table) do
        type_name = tostring(peripheral.getType(val))
        
        if string.find(type_name, target) then
            print("Found <", type_name, "> at", val)
            
            reference = peripheral.wrap(val)
            return reference
        end
    end
    if skip_error == false then
        error("No cell is found, exiting.")
    end
    return false
    
end


local function fetch_cell_reference()
    return fetch_reference(cell_ident, false)
end


local function fetch_monitor_reference()
    return fetch_reference(monitor_ident, true)
end


local function cal_energy_percent(cell_reference)
    cap = cell_reference.getEnergyCapacity()
    cur = cell_reference.getEnergy()
    percent = (cur / cap) * 100
    return percent
end


local function rewrite_last()
    x, y = term.getCursorPos()
    term.setCursorPos(1, y - 1)
end


local function timer(n)
    print()
    
    for i=0, 4 do
        rewrite_last()
        print("Will now start in", n - i)
        os.sleep(1)
    end
end


local function main()
    cell_ref = fetch_cell_reference()
    monitor_ref = fetch_monitor_reference()
    timer(5)
    clear()
    
    print(os.day(), "D | Started    | PWR_MAX", cell_ref.getEnergyCapacity())
    print()
    print()
    
    local last_state = 0
    local started = false
    
    -- dirtiest block I've ever written?
    while true do
        local new = cal_energy_percent(cell_ref)
        local formatted = string.format("%.2f %%", new)
        
        -- update monitor if it exists, else try finding it again.
        if monitor_ref == false then
            monitor_ref = fetch_monitor_reference()
        else
            monitor_ref.setTextScale(2)  -- bad!
            monitor_ref.write(string.format("%.2f", new))
        end
        
        -- check state and set action accordingly.
        if new < low_watermark then  -- state 1
            if last_state == 1 then
                rewrite_last()
            end
                
            print(os.day(), "D | Engine on  | PWR:", formatted)
            redstone.setAnalogOutput(redstone_location, redstone_emit_level)
            last_state = 1
            started = true
            
        elseif new > high_watermark then  -- state 2
            if last_state == 2 then
                rewrite_last()
            end
            
            print(os.day(), "D | Engine off | PWR:", formatted)
            redstone.setAnalogOutput(redstone_location, redstone_off_level)
            last_state = 2
            started = false
            
        elseif started == true then  -- state 3
            if last_state == 3 or last_state == 1 then
                rewrite_last()
            end
            
            print(os.day(), "D | Engine on  | PWR:", formatted)
            last_state = 3
            
        elseif started == false then  -- state 4
            if last_state == 4 or last_state == 2  then
                rewrite_last()
            end
            
            print(os.day(), "D | Engine off | PWR:", formatted)
            last_state = 4
        end
        
        os.sleep(check_interval)
    end
end


-- boilerplate
clear()
main()

