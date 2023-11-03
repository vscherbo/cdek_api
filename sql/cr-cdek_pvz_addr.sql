DROP FUNCTION shp.cdek_pvz_addr(shp_id varchar);

CREATE OR REPLACE FUNCTION shp.cdek_pvz_addr(pvz varchar)
 RETURNS character varying
 LANGUAGE plpgsql
AS $function$
DECLARE
res_to varchar;

begin
--SELECT cdek_pvz.fulladdress INTO res_to
-- SELECT format('%s, %s', cdek_pvz.city, cdek_pvz.address) INTO res_to
SELECT cdek_pvz.city_code INTO res_to
FROM cdek_pvz
WHERE cdek_pvz.pvz_code = pvz;

return res_to;

end;
$function$
;
