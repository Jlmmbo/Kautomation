function getlowestfuel{
    parameter part.
    set resources to part:resources.
    if resources:length = 0 {
        return 100.
    }
    local lowest is 100000000.
    from {local idx is 0.} until idx = resources:length - 1 step {set idx to idx + 1.} do {
        if (resources[idx]:name = "LiquidFuel") or (resources[idx]:name = "SolidFuel") {
            set fuel to resources[idx]:amount.
            if fuel < lowest {
                set lowest to fuel.
            }
        }
    }
    return lowest.
}

function checkfuel {// check if there are any empty fuel tanks, if so stage (assume it decouples the first to empty)
    from {local idx is 0.} until idx = ship:parts:length - 1 step {set idx to idx + 1.} do {
        set part to ship:parts[idx].
        set fuel to getlowestfuel(part).
        if fuel < .1 {
                print "empty fuel tank" + part:title.
                stage.
                return.
        }
    }
}