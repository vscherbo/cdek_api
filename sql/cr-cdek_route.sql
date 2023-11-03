CREATE OR REPLACE FUNCTION shp.cdek_route(shpid integer)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
declare
tn varchar;

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
if shpid <= 0 then
    return shp.stub_cdek_route(shpid);
else
    SELECT d.term_name INTO tn 
    FROM ship_bills sb JOIN delivery d ON sb.dlvrid = d.dlvr_id
    WHERE d.carr_id=44 AND sb.shp_id=shpid;
    if tn='до двери' then
        return 137;
    else
        return 136;
    end if;
end if;

end;
$function$
;
