from .file_utils import generate_survey_from_file


def main():
    file_path = "/root/talk/design/慢病随访调查问卷.pdf"

    try:
        survey = generate_survey_from_file(file_path)

        with open("Q.txt", 'w', encoding='utf-8') as fw:
            print("调查问卷已生成")
            fw.write(survey)

    except Exception as e:
        print(f"生成调查问卷时发生错误：{e}")


# 当文件作为脚本运行时，执行主函数
if __name__ == "__main__":
    main()
