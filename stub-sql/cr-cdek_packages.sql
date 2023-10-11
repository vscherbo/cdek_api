DROP FUNCTION shp.cdek_packages(shp_id integer);

CREATE OR REPLACE FUNCTION shp.cdek_packages(shp_id integer)
RETURNS TABLE (
    "number" varchar(255), 
    weight integer, -- вес в граммах
    length integer, -- длина в сантиметрах
    width integer, -- ширина в сантиметрах
    height integer -- выслта в сантиметрах
)
LANGUAGE plpgsql
AS $function$
begin
if shp_id = 111 then
    return query 
    VALUES('коробка 1'::varchar, 500, 10, 20, 30);
else
    return query 
    VALUES('коробка 1'::varchar, 700, 10, 20, 30), ('коробка 2'::varchar, 1000, 11, 22, 33);
end if;

end;
$function$
;
--        VALUES('прибор1', 123456789, VALUES(0), 1234, 200, 2)
