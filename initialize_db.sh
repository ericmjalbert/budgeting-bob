#!/bin/bash
heroku pg:psql -c "
    CREATE TABLE IF NOT EXISTS public.user (
        id SERIAL PRIMARY KEY , 
        username TEXT UNIQUE NOT NULL, 
        password TEXT NOT NULL 
    );"
    
