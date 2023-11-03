DROP FUNCTION shp.cdek_recipient_phones(integer);

CREATE OR REPLACE FUNCTION shp.cdek_recipient_phones(shpid integer)
 RETURNS TABLE(number character varying, additional character varying)
 LANGUAGE plpgsql
AS $function$
begin
if shpid <= 0 then -- DEBUG
    return query select * from shp.stub_cdek_recipient_phones(shpid); 
else --prod
    return query 
        SELECT DISTINCT ('+' || p.phn_dl)::varchar, p.phn_additional::varchar
        FROM ship_phones AS p INNER JOIN (delivery AS d INNER JOIN ship_bills AS b ON d.dlvr_id = b.dlvrid) ON p.dlvr_id = d.dlvr_id
        WHERE b.shp_id=shpid;
end if; --prod
end;
$function$
;

