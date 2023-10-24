DROP FUNCTION shp.cdek_packages(shp_id integer);

CREATE OR REPLACE FUNCTION shp.cdek_packages(shp_id integer)
 RETURNS TABLE(number character varying, weight integer, length integer, width integer, height integer)
 LANGUAGE plpgsql
AS $function$
begin
if shp_id < 0 then -- DEBUG
    if shp_id = -111 then
        return query 
        VALUES('коробка 1'::varchar, 500, 10, 20, 30);
    else
        return query 
        VALUES('коробка 1'::varchar, 700, 10, 20, 30), ('коробка 2'::varchar, 1000, 11, 22, 33);
    end if; -- shp_id=-111
else -- production
SELECT 
-- ('коробка ' || ship_wlwh.box)::varchar, sb.bill 
(format('%s-', sb.bill) || ship_wlwh.box)::varchar
, ship_wlwh.wt, ship_wlwh.lh, ship_wlwh.wh, ship_wlwh.ht
    FROM ship_wlwh
    join ship_bills sb on 
    --sb.shp_id = ship_wlwh.shp_id and 
    sb.bill = (select bill from ship_bills where shp_id = shp_id order by bill limit 1)
    WHERE ship_wlwh.shp_id=shp_id
    ORDER BY ship_wlwh.box;
end if;

end;
$function$
;
