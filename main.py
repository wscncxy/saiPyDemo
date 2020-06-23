import MysqlUtil
from CsvUtils import CsvUtils
# mysqlUtil = MysqlUtil.MysqlUtil("db.saiarea.com", "sai", "F8@9eca&kc3fCdas", "sai_area");
# mysqlUtil.con()
# result = mysqlUtil.query(("select * from role_info"),())
# for (role_name) in result:
#     print("{}".format(role_name))
# mysqlUtil.close()
def main():
    csvUtils=CsvUtils("test.csv");
    csvUtils.read()


if __name__ == '__main__':
    main()