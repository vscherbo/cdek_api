DROP FUNCTION shp.cdek_packages(shp_id integer);

CREATE OR REPLACE FUNCTION shp.cdek_packages(arg_shp_id integer)
 RETURNS TABLE(number character varying, weight integer, length integer, width integer, height integer)
 LANGUAGE plpgsql
AS $function$
begin
if arg_shp_id < 0 then -- DEBUG
    return query
    select * from shp.stub_cdek_packages(arg_shp_id);
else -- production
return query
SELECT 
-- ('коробка ' || ship_wlwh.box)::varchar, sb.bill 
(format('%s-', sb.bill) || ship_wlwh.box)::varchar
, ship_wlwh.wt, ship_wlwh.lh, ship_wlwh.wh, ship_wlwh.ht
    FROM ship_wlwh
    join ship_bills sb on 
    sb.bill = (select bill from ship_bills where ship_bills.shp_id = arg_shp_id order by bill limit 1)
    WHERE ship_wlwh.shp_id=arg_shp_id
    ORDER BY ship_wlwh.box;
end if;

end;
$function$
;
