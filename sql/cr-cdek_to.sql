DROP FUNCTION shp.cdek_to(shp_id integer);

CREATE OR REPLACE FUNCTION shp.cdek_to(shpid integer)
 RETURNS character varying
 LANGUAGE plpgsql
AS $function$
DECLARE
res_to varchar;
tn varchar;

begin
if shpid <= 0 then
    res_to := shp.stub_cdek_to(shpid);
else
    SELECT d.term_name, d.dest_addr INTO tn, res_to 
    FROM ship_bills sb JOIN delivery d ON sb.dlvrid = d.dlvr_id
    WHERE d.carr_id=44 AND sb.shp_id=shpid;
    if tn<>'до двери' then
        SELECT cdek_pvz.pvz_code INTO res_to
        FROM cdek_pvz
        WHERE cdek_pvz.pvz_name=tn;
    end if;
    if res_to Is Null OR res_to='' then 
        res_to='не определен';
    end if;

end if; -- PROD, not stub

return res_to;

end;
$function$
;
