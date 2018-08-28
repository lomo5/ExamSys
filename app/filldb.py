import os
from datetime import datetime

import xlrd

from . import db
from .models import QuestionType, Question, Role, User, Subject, Department


class FillDb:
    xlsx_name = {"question_type": "题型.xlsx", "question": "题库.xlsx", "role": "角色.xlsx", "user": "用户.xlsx",
                 "subject": "科目.xlsx", "department": "部门.xlsx"}

    @staticmethod
    def create_db():
        db.create_all()

    def fill_subject(self):
        xls = self.xlsx_name['subject']
        obj = Subject()

        try:
            wbk = xlrd.open_workbook(xls, encoding_override="utf-8")
        except:
            print('excel文件"%s"不存在！' % xls)
            return

        try:
            sh = wbk.sheets()[0]  # 因为Excel里只有sheet1有数据，如果都有可以使用注释掉的语句
            # sh = bk.sheet_by_name("xxxxx.xlsx")
        except:
            print("no sheet in %s named sheet1" % xls)
        else:
            nrows = sh.nrows
            ncols = sh.ncols
            print(os.getcwd(), "行数 %d,列数 %d" % (nrows, ncols))
            for i in range(1, nrows):
                row_data = sh.row_values(i)

                obj.id = row_data[0]
                obj.subject_name = row_data[1]

                db.session.add(obj)

            db.session.commit()
            db.session.close()

        count = obj.query.all().count()
        print(count)

    def fill_user(self):
        xls = self.xlsx_name['user']

        try:
            wbk = xlrd.open_workbook(xls, encoding_override="utf-8")
        except:
            print('excel文件"%s"不存在！' % xls)
            return

        try:
            sh = wbk.sheets()[0]  # 因为Excel里只有sheet1有数据，如果都有可以使用注释掉的语句
            # sh = bk.sheet_by_name("benke.xlsx")
        except:
            print("no sheet in %s named sheet1" % xls)
        else:
            nrows = sh.nrows
            ncols = sh.ncols
            print(os.getcwd(), "行数 %d,列数 %d" % (nrows, ncols))
            oid = 0  # 初始化id
            table_len = len(User.query.all())
            if table_len == 0:  # 如果表中没有数据，则id从1开始递增，否则不指定ID，有数据库自增生成。
                for i in range(1, nrows):
                    row_data = sh.row_values(i)
                    print(row_data)
                    obj = User()
                    oid += 1  # ID从1开始
                    obj.id = oid
                    obj.staff_number = str(row_data[1])
                    obj.username = str(row_data[2])
                    obj.department_id = Department.query.filter_by(department_name=row_data[3]).first().id
                    obj.role_id = Role.query.filter_by(role_name=row_data[4]).first().id
                    obj.add_time = datetime.utcnow()
                    obj.password = str(row_data[5])
                    obj.info = str(row_data[8])

                    db.session.add(obj)
            else:  # 如果表中已有数据，则不指定id，由数据库自增生成
                for i in range(1, nrows):
                    row_data = sh.row_values(i)
                    print(row_data)
                    obj = User()
                    obj.staff_number = str(row_data[1])
                    obj.username = str(row_data[2])
                    obj.department_id = Department.query.filter_by(department_name=row_data[3]).first().id
                    obj.role_id = Role.query.filter_by(role_name=row_data[4]).first().id
                    obj.add_time = datetime.utcnow()
                    obj.password = str(row_data[5])
                    obj.info = str(row_data[8])

                    db.session.add(obj)

            db.session.commit()
            db.session.close()

        count = len(User.query.all())
        print('共插入%d行。' % count)

    def fill_question(self):
        xls = self.xlsx_name['question']

        try:
            wbk = xlrd.open_workbook(xls, encoding_override="utf-8")
        except:
            print('excel文件"%s"不存在！' % xls)
            return

        try:
            sh = wbk.sheets()[0]  # 取得sheet
        except:
            print("no sheet in %s named sheet1" % xls)
        else:
            nrows = sh.nrows
            ncols = sh.ncols
            print(os.getcwd(), "行数 %d,列数 %d" % (nrows, ncols))
            oid = 0
            table_len = len(Question.query.all())  # 表中已有数据数量
            if table_len == 0:  # 如果表中没有数据，则id从1开始递增，否则不指定ID，有数据库自增生成。
                for i in range(1, nrows):
                    row_data = sh.row_values(i)
                    print(row_data)
                    obj = Question()
                    oid += 1
                    obj.id = oid
                    # 由于id是自增的，因此这里不需要指定id。但是如果之前导过数据又删除了，则不会复用空出来的ID。
                    obj.subject_id = Subject.query.filter_by(subject_name=row_data[0]).first().id
                    obj.qtype_id = QuestionType.query.filter_by(type_name=row_data[1]).first().id
                    obj.question = row_data[2]
                    option = str(row_data[3])
                    for opt in range(4, 11):  # 生成options字串
                        if str(row_data[opt]) != '':
                            option = option + "||" + str(row_data[opt])
                    obj.options = option
                    obj.answer = str(row_data[11])
                    obj.info = str(row_data[12])
                    obj.add_time = datetime.utcnow()
                    db.session.add(obj)
            else:
                for i in range(1, nrows):
                    row_data = sh.row_values(i)
                    print(row_data)
                    obj = Question()
                    # 由于id是自增的，因此这里不需要指定id。但是如果之前导过数据又删除了，则不会复用空出来的ID。
                    obj.subject_id = Subject.query.filter_by(subject_name=row_data[0]).first().id
                    obj.qtype_id = QuestionType.query.filter_by(type_name=row_data[1]).first().id
                    obj.question = row_data[2]
                    option = str(row_data[3])
                    for opt in range(4, 11):  # 生成options字串
                        if str(row_data[opt]) != '':
                            option = option + "||" + str(row_data[opt])
                    obj.options = option
                    obj.answer = str(row_data[11])
                    obj.info = str(row_data[12])
                    obj.add_time = datetime.utcnow()
                    db.session.add(obj)

            db.session.commit()
            db.session.close()

        count = len(db.session.query(Question).all())  # len(Question.query.all())  # 两种方法均可。
        print('共插入%d行。' % count)

    #  向usersubject表中插入数据
    def fill_usersubject(self):
        sub_list=Subject.query.all()
        print('共有%d个Subject。' % len(sub_list))
        users = User.query.all()
        print('共有%d个user。' % len(users))
        for u in users:
            u.subjects=sub_list
            db.session.add(u)
        db.session.commit()
        db.session.close()

    # 为单个用户添加所有subject
    def add_subject(self, user):
        sub_list = Subject.query.all()
        print('共有%d个Subject。' % len(sub_list))
        user.subjects = sub_list
        db.session.add(user)
        db.session.commit()
        db.session.close()

