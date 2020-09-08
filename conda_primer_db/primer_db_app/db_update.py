from sqlalchemy import create_engine, engine_from_config, MetaData, Table, Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Time, Date, UniqueConstraint, not_, and_, select, join, outerjoin, update, func
from sqlalchemy.dialects.mssql import \
    BIGINT, BINARY, BIT, CHAR, DATE, DATETIME, DATETIME2, \
    DATETIMEOFFSET, DECIMAL, FLOAT, IMAGE, INTEGER, MONEY, \
    NCHAR, NTEXT, NUMERIC, NVARCHAR, REAL, SMALLDATETIME, \
    SMALLINT, SMALLMONEY, SQL_VARIANT, TEXT, TIME, \
    TIMESTAMP, TINYINT, UNIQUEIDENTIFIER, VARBINARY, VARCHAR
import os
import pdb
import datetime

db_path=os.path.join(os.getcwd(),"db.sqlite3")
engine = create_engine("sqlite:///" + db_path)
metadata = MetaData()

auth_user = Table("auth_user", metadata,
                  Column("id", Integer, primary_key=True),
                  Column("first_name", String(30)),
                  Column("last_name", String(30)))

primer_db_site_imported_by = Table("primer_db_site_imported_by", metadata,
                                   Column("id", Integer, primary_key=True),
                                   Column("imported_by", String(30)),
                                   Column("status", String(10)))
primer_db_site_primer = Table("primer_db_site_primer", metadata,
                              Column("id", Integer, primary_key=True),
                              Column("imported_by_id_id", String(30)),
                              Column("date_imported", String(30)),
                              Column("date_archived", String(30)),
                              Column("date_order_placed", String(30)),
                              Column("date_order_recieved", String(30)),
                              Column("date_testing_completed", String(30)),
                              Column("date_retesting_completed", String(30)),
                              Column("direction", String(10)),
                              Column("new_direction_id", Integer),
                              Column("modification", String(10)),
                              Column("modification_5", String(10)),
                              Column("new_modification_id", Integer),
                              Column("new_modification_5_id", Integer),
                              Column("archived_by_id_id", String(30)))

primer_db_site_modification = Table("primer_db_site_modification", metadata,
                                   Column("id", Integer, primary_key=True),
                                   Column("modification", String(10)))

primer_db_site_direction = Table("primer_db_site_direction", metadata,
                                   Column("id", Integer, primary_key=True),
                                   Column("direction", String(10)))

with engine.connect() as conn:
    #sets everything to KH (for testing)
    # to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.imported_by_id_id is not None). \
    #             values(imported_by_id_id=43)
    # conn.execute(to_update)
    #
    # to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.archived_by_id_id is not None). \
    #             values(archived_by_id_id=43)
    # conn.execute(to_update)
    # sql=select([auth_user.c.id.label("User_ID"), auth_user.c.first_name.label("first_name"), auth_user.c.last_name.label("last_name")]). \
    #     select_from(auth_user). \
    #     where(auth_user.c.id is not None)
    # django_users=[dict(row) for row in conn.execute(sql)]
    #
    # sql=select([primer_db_site_imported_by.c.id.label("User_ID"), primer_db_site_imported_by.c.imported_by.label("imported_name")]). \
    #     select_from(primer_db_site_imported_by). \
    #     where(primer_db_site_imported_by.c.id is not None)
    # primer_users=[dict(row) for row in conn.execute(sql)]
    # imported_to_django={}
    # for user in primer_users:
    #     try:
    #         first, last = user["imported_name"].split(" ")
    #     except:
    #         first, last = "HISTORICAL", "DATA"
    #     for django_user in django_users:
    #         if django_user["first_name"]==first and django_user["last_name"]==last:
    #             imported_to_django[user["User_ID"]]=django_user["User_ID"]
    # for old, new in imported_to_django.items():
    #     to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.imported_by_id_id==old). \
    #                 values(imported_by_id_id=new)
    #     conn.execute(to_update)
    #     to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.archived_by_id_id==old). \
    #                 values(archived_by_id_id=new)
    #     conn.execute(to_update)
    # #corrects dates to python date format (not done all together as date_imported may be one style and date_archived another
    # sql=select([primer_db_site_primer.c.id, primer_db_site_primer.c.date_imported]). \
    #      select_from(primer_db_site_primer). \
    #      where(primer_db_site_primer.c.id is not None)
    # dates=[dict(row) for row in conn.execute(sql)]
    #
    # for entry in dates:
    #     try:
    #         to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                    values(date_imported=datetime.datetime.strptime(entry["date_imported"],"%d/%m/%Y").date())
    #         conn.execute(to_update)
    #     except:
    #         try:
    #             to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                        values(date_imported=datetime.datetime.strptime(entry["date_imported"],"%d/%m/%y").date())
    #             conn.execute(to_update)
    #         except:
    #             to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                    values(date_imported=None)
    #             conn.execute(to_update)
    #
    # sql=select([primer_db_site_primer.c.id, primer_db_site_primer.c.date_archived]). \
    #      select_from(primer_db_site_primer). \
    #      where(primer_db_site_primer.c.id is not None)
    # dates=[dict(row) for row in conn.execute(sql)]
    #
    # for entry in dates:
    #     try:
    #         to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                    values(date_archived=datetime.datetime.strptime(entry["date_archived"],"%d/%m/%Y").date())
    #         conn.execute(to_update)
    #     except:
    #         try:
    #             to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                        values(date_archived=datetime.datetime.strptime(entry["date_archived"],"%d/%m/%y").date())
    #             conn.execute(to_update)
    #         except:
    #             to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                    values(date_archived=None)
    #             conn.execute(to_update)
    # sql=select([primer_db_site_primer.c.id, primer_db_site_primer.c.date_order_placed]). \
    #      select_from(primer_db_site_primer). \
    #      where(primer_db_site_primer.c.id is not None)
    # dates=[dict(row) for row in conn.execute(sql)]
    #
    # for entry in dates:
    #     try:
    #         to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                    values(date_order_placed=datetime.datetime.strptime(entry["date_order_placed"],"%d/%m/%Y").date())
    #         conn.execute(to_update)
    #     except:
    #         try:
    #             to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                        values(date_order_placed=datetime.datetime.strptime(entry["date_order_placed"],"%d/%m/%y").date())
    #             conn.execute(to_update)
    #         except:
    #             to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                    values(date_order_placed=None)
    #             conn.execute(to_update)
    # sql=select([primer_db_site_primer.c.id, primer_db_site_primer.c.date_order_recieved]). \
    #      select_from(primer_db_site_primer). \
    #      where(primer_db_site_primer.c.id is not None)
    # dates=[dict(row) for row in conn.execute(sql)]
    #
    # for entry in dates:
    #     try:
    #         to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                    values(date_order_recieved=datetime.datetime.strptime(entry["date_order_recieved"],"%d/%m/%Y").date())
    #         conn.execute(to_update)
    #     except:
    #         try:
    #             to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                        values(date_order_recieved=datetime.datetime.strptime(entry["date_order_recieved"],"%d/%m/%y").date())
    #             conn.execute(to_update)
    #         except:
    #             to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                    values(date_order_recieved=None)
    #             conn.execute(to_update)
    # sql=select([primer_db_site_primer.c.id, primer_db_site_primer.c.date_testing_completed]). \
    #      select_from(primer_db_site_primer). \
    #      where(primer_db_site_primer.c.id is not None)
    # dates=[dict(row) for row in conn.execute(sql)]
    #
    # for entry in dates:
    #     try:
    #         to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                    values(date_testing_completed=datetime.datetime.strptime(entry["date_testing_completed"],"%d/%m/%Y").date())
    #         conn.execute(to_update)
    #     except:
    #         try:
    #             to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                        values(date_testing_completed=datetime.datetime.strptime(entry["date_testing_completed"],"%d/%m/%y").date())
    #             conn.execute(to_update)
    #         except:
    #             to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                    values(date_testing_completed=None)
    #             conn.execute(to_update)
    # sql=select([primer_db_site_primer.c.id, primer_db_site_primer.c.date_retesting_completed]). \
    #      select_from(primer_db_site_primer). \
    #      where(primer_db_site_primer.c.id is not None)
    # dates=[dict(row) for row in conn.execute(sql)]
    #
    # for entry in dates:
    #     try:
    #         to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                    values(date_retesting_completed=datetime.datetime.strptime(entry["date_retesting_completed"],"%d/%m/%Y").date())
    #         conn.execute(to_update)
    #     except:
    #         try:
    #             to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                        values(date_retesting_completed=datetime.datetime.strptime(entry["date_retesting_completed"],"%d/%m/%y").date())
    #             conn.execute(to_update)
    #         except:
    #             to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.id==entry["id"]). \
    #                    values(date_retesting_completed=None)
    #             conn.execute(to_update)

    # sql = select([primer_db_site_modification.c.id, primer_db_site_modification.c.modification]). \
    #       select_from(primer_db_site_modification). \
    #       where(primer_db_site_modification.c.id is not None)
    # mods={k:v for k,v in conn.execute(sql)}
    # for key, mod in mods.items():
    #     to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.modification==mod).\
    #     values(new_modification_id=key)
    #     conn.execute(to_update)
    #     to_update=update(primer_db_site_primer).where(primer_db_site_primer.c.modification_5==mod).\
    #     values(new_modification_5_id=key)
    #     conn.execute(to_update)
    sql = select([primer_db_site_direction.c.id, primer_db_site_direction.c.direction]). \
          select_from(primer_db_site_direction). \
          where(primer_db_site_direction.c.id is not None)
    mods={k:v for k,v in conn.execute(sql)}
    for key, mod in mods.items():
        to_update=update(primer_db_site_primer).where(func.upper(primer_db_site_primer.c.direction)==func.upper(mod.upper())).\
        values(new_direction_id=key)
        conn.execute(to_update)

