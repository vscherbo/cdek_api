CREATE OR REPLACE FUNCTION shp.cdek_package_items(shp_id integer)
RETURNS TABLE (phone varchar(255), additional varchar (255))
LANGUAGE plpgsql
AS $function$
begin
if shp_id = 111 then
    return query 
    VALUES
    ('прибор1', --name
        123456789, -- KC
        1234, -- cost
        200, -- weight
        2 -- amount
    );
else
    return query 
    VALUES
    ('Катушка', --name
        000000001, -- KC
        1111, -- cost
        220, -- weight
        1 -- amount
    )
    ,
    ('Клапан', --name
        0000000022, -- KC
        1001, -- cost
        123, -- weight
        2 -- amount
    )
    ;
end if;

end;
$function$
;
