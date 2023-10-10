CREATE OR REPLACE FUNCTION shp.cdek_route(shp_id integer)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
begin
/*
для ИМ type:1 
137: С-Д
136: С-С
138: Д-С
139: Д-Д

для Доставки type:2
480 (Д-Д)
481 (Д-С)
482 (С-Д)
483 (С-С)
*/  

    
    return 137;
end;
$function$
;
