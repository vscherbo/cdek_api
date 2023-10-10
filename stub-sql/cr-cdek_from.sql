CREATE OR REPLACE FUNCTION shp.cdek_from(shp_id integer)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE
res_from varchar;
begin
if shp_id = 111 then
    res_from = 'SPB9';
else
    res_from = 'СПБ, улица, дом';
end if;

return res_from;
end;
$function$
;
