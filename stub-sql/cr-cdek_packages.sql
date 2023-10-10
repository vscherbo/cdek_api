CREATE OR REPLACE FUNCTION shp.cdek_packages(shp_id integer)
RETURNS TABLE (phone varchar(255), additional varchar (255))
LANGUAGE plpgsql
AS $function$
begin
if shp_id = 111 then
    return query 
    VALUES('коробка 1', 500, 10, 20, 30, 'Комментарий');
else
    return query 
    VALUES('коробка 1', 700, 10, 20, 30, 'Комментарий'), ('коробка 2', 1000, 11, 22, 33, 'Каммент');
end if;

end;
$function$
;
--        VALUES('прибор1', 123456789, VALUES(0), 1234, 200, 2)
