package com.supermarket.auth.common;

import java.util.HashMap;

public class Result extends HashMap<String, Object> {
    
    public static Result ok() {
        Result r = new Result();
        r.put("code", 0);
        r.put("msg", "success");
        return r;
    }

    public static Result fail(String msg) {
        Result r = new Result();
        r.put("code", 500);
        r.put("msg", msg);
        return r;
    }

    @Override
    public Result put(String key, Object value) {
        super.put(key, value);
        return this;
    }
}
