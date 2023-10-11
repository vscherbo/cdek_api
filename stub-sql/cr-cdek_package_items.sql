DROP FUNCTION shp.cdek_package_items(shp_id integer);

CREATE OR REPLACE FUNCTION shp.cdek_package_items(shp_id integer)
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
if shp_id = 111 then
    return query 
    VALUES
    ('прибор1'::varchar, --name
        123456789::varchar, -- KC
        1234.0, -- cost
        200, -- weight
        2 -- amount
    );
else
    return query 
    VALUES
    ('Катушка'::varchar, --name
        000000001::varchar, -- KC
        1111.0, -- cost
        220, -- weight
        1 -- amount
    )
    ,
    ('Клапан'::varchar, --name
        0000000022::varchar, -- KC
        1001.0, -- cost
        123, -- weight
        2 -- amount
    )
    ;
end if;

end;
$function$
;
