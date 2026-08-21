function clamp{
    parameter mn.
    parameter mx.
    parameter val.

    return(max(min(val,mx),mn)).
}

function within_err{
    parameter epsilon.
    parameter tgt.
    parameter value.
    if (tgt - value > epsilon){
        return 0.
    }
    if (value - tgt > epsilon){
        return 0.
    }
    return 1.
}