/*
Brenton Klassen
08/01/2014
Import data from Snail
*/

use Snail
go

/***************************
BULK INSERT ORDERS FROM FILE
***************************/

insert into [Order]
(merchant,completeOrderReference,shortOrderReference,merchantID,
dateStamp,fullName,phoneNumber,emailAddress,address1,
address2,address3,town,region,postCode,country,packingSlip)
select distinct f.merchant,
f.completeOrderReference,
f.shortOrderReference,
f.merchantID,
getdate() as dateStamp,
left(upper(f.fullName),40) as fullName,
left(f.phoneNumber,16) as phoneNumber,
left(upper(f.emailAddress),40) as emailAddress,
left(upper(f.address1),100) as address1,
left(upper(f.address2),40) as address2,
left(upper(f.address3),40) as address3,
left(upper(f.town),40) as town,
f.region, /* validated by Python */
f.postCode, /* validated by Python */
f.country, /* validate by Python */
f.packingSlip
from OrderFile as f
left join [Order] as o
	on f.merchantID = o.merchantID and f.completeOrderReference = o.completeOrderReference
where o.orderId is null


insert into Item
(merchantID,shortOrderReference,lineNumber,dateStamp,itemTitle,itemSKU,
itemQuantity,itemUnitCost,itemAttribKey,itemAttribVal)
select distinct f.merchantID,
f.shortOrderReference,
f.lineNumber,
getdate() as dateStamp,
left(f.itemTitle,300) as itemTitle,
f.itemSKU,
f.itemQuantity,
f.itemUnitCost,
f.itemAttribKey,
f.itemAttribVal
from ItemFile as f
left join Item as i
	on f.merchantID = i.merchantID and f.shortOrderReference = i.shortOrderReference and f.lineNumber = i.lineNumber and coalesce(f.itemAttribKey,'') = coalesce(i.itemAttribKey,'')
where i.itemId is null


/************************************
BULK INSERT PACKAGE DETAILS FROM FILE
************************************/

insert into Package
(shortOrderReference,merchantID,dateStamp,returnCompany,returnAdd1,returnAdd2,returnCity,
returnState,returnZip,packageNumber,carrier,serviceClass,[length],width,height,[weight],[bulk],note)
select distinct f.shortOrderReference,
f.merchantID,
GETDATE() as dateStamp,
f.returnCompany,
f.returnAdd1,
f.returnAdd2,
f.returnCity,
f.returnState,
f.returnZip,
coalesce(f.packageNumber,1) as packageNumber,
f.carrier,
f.serviceClass,
f.[length],
f.width,
f.height,
f.[weight],
f.[bulk],
f.note
from PackageFile as f
left join Package as p
	on f.merchantID = p.merchantID and f.shortOrderReference = p.shortOrderReference
where p.packageId is null


/******************************
BULK INSERT SHIPMENTS FROM FILE
******************************/

insert into Shipment
(merchantID,shortOrderReference,packageNumber,dateStamp,carrier,serviceClass,postage,trackingNumber,billedWeight)
select f.merchantID,
f.shortOrderReference,
coalesce(f.packageNumber,1) as packageNumber,
getdate() as dateStamp,
f.carrier,
f.serviceClass,
f.postage,
f.trackingNumber,
f.billedWeight
from ShipmentFile as f
left join Shipment as s
	on f.merchantID = s.merchantID and f.shortOrderReference = s.shortOrderReference and coalesce(f.packageNumber,1) = s.packageNumber
where s.ShipmentId is null

