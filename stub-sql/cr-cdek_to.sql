DROP FUNCTION shp.cdek_to(shp_id integer);

CREATE OR REPLACE FUNCTION shp.cdek_to(shp_id integer)
 RETURNS varchar
 LANGUAGE plpgsql
AS $function$
DECLARE
res_to varchar;
begin
if shp_id = 111 then
    res_to = 'MSK67';
else
    res_to = '443045, Самарская обл, г.о. Самара, вн.р-н Октябрьский, г. Самара, проезд 3-й, д. 50б, помещ. 2';
end if;

return res_to;
end;
$function$
;
