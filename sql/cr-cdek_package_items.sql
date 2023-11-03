DROP FUNCTION shp.cdek_package_items(integer);

CREATE OR REPLACE FUNCTION shp.cdek_package_items(arg_shp_id integer)
RETURNS TABLE (
    "name" varchar(255),
    ware_key varchar (20),
    cost numeric,
    weight integer,
    amount integer
)
LANGUAGE plpgsql
AS $function$
begin
if arg_shp_id <= 0 then
    return query select * from shp.stub_cdek_package_items(arg_shp_id);
else        
    return query 
    select 
    substring(bc."Наименование", 1, 255)::varchar(255) as "name",
    bc."КодСодержания"::varchar(20) as ware_key, 
    bc."ЦенаНДС"::numeric as cost, 
    coalesce(round(greatest  (c."Нетто" , c."Брутто")::numeric), 100)::integer as weight,
    -- round(greatest  (c."Нетто" , c."Брутто")::numeric)::integer as weight,
    bc."Кол-во"::integer as amount
    from ship_bills sb 
    join "Содержание счета" bc on bc."№ счета" = sb.bill 
    join "Содержание" c on c."КодСодержания" = bc."КодСодержания"
    where sb.shp_id = arg_shp_id;
end if;

end;
$function$
;
