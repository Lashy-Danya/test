SELECT * FROM products;
SELECT * FROM product_type;
SELECT * FROM product_technical_data;
SELECT * FROM product_technical_data_value;

-- Получение характеристик товара (возможно)
SELECT td.name, tdv.value, tdv.product_id
FROM product_technical_data_value AS tdv
JOIN product_technical_data as td ON tdv.technical_data_id = td.id;

-- Получение тип товара
SELECT p.id, pt.name
FROM products AS p
JOIN product_type AS pt ON p.product_type_id = pt.id;

-- функция получения типа товара по его id
CREATE OR REPLACE FUNCTION type_product(id_product int)
RETURNS text AS $$
	SELECT pt.name
	FROM products AS p
	JOIN product_type AS pt ON p.product_type_id = pt.id
	WHERE p.id = id_product;
$$ LANGUAGE 'sql';

SELECT type_product('2');

-- функция получения характеристик и их значения для товара по его id
CREATE OR REPLACE FUNCTION data_value_product(id_product int)
RETURNS TABLE (
	name text,
	value text
) AS $$
DECLARE
	temp_info record;
BEGIN
	FOR temp_info IN (SELECT td.name, tdv.value, tdv.product_id
					FROM product_technical_data_value AS tdv
					JOIN product_technical_data as td ON tdv.technical_data_id = td.id
					WHERE tdv.product_id = id_product)
		LOOP
			name = temp_info.name;
			value = temp_info.value;
			RETURN NEXT;
		END LOOP;
END; $$ LANGUAGE 'plpgsql';

SELECT data_value_product(2);