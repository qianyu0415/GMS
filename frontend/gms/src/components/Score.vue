<template>
    <div>
      <el-card class="cardStyle" v-loading="loading">
        <!-- 功能按钮 -->
        <el-button @click="change" size="small" style="margin-bottom: 15px">筛选</el-button>
        <el-button @click="batchMethod" type="info" size="small" :disabled="dataTable.length <= 0" style="margin-bottom: 15px">批量编辑</el-button>
        <el-button @click="addEntry" type="primary" size="small" style="margin-bottom: 15px">成绩录入</el-button>
        <el-button @click="exportMethod" type="success" :disabled="dataTable.length <= 0" size="small" style="margin-bottom: 15px">导出</el-button>
        <el-button
          @click="batchDelete"
          type="danger"
          size="small"
          :disabled="selection.length === 0"
          style="margin-bottom: 15px"
        >批量删除</el-button>
  
        <!-- 过滤框 -->
        <el-collapse-transition>
          <div v-if="show" style="background-color: white; height: 100px; box-sizing: border-box">
            <el-form ref="form" :model="form" label-width="80px">
              <el-row>
                <el-col :span="8">
                  <el-form-item label="学年：">
                    <el-select v-model="form.year" style="width: 90%">
                      <el-option v-for="item in yearArr" :key="item.value" :label="item.label" :value="item.value"></el-option>
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="学期：">
                    <el-select v-model="form.term" style="width: 90%">
                      <el-option v-for="item in termArr" :key="item.value" :label="item.label" :value="item.value"></el-option>
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="专业：" prop="profession">
                    <el-select v-model="form.professionObj" style="width: 90%" @change="professionChange" value-key="profession">
                      <el-option v-for="item in classArr" :key="item.profession" :label="item.profession" :value="item"></el-option>
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row>
                <el-col :span="8">
                  <el-form-item label="类别：" prop="grade">
                    <el-select v-model="form.grade" style="width: 90%">
                      <el-option v-for="(item, index) in categoryOptions" :key="index" :label="item" :value="item"></el-option>
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="课程名：" prop="courseName">
                    <el-select v-model="form.courseName" style="width: 90%">
                      <el-option v-for="item in courseArr" :key="item" :label="item" :value="item"></el-option>
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8" style="text-align: right;">
                  <el-button type="primary" @click="clickAndClose" size="small" style="margin-right: 10px">确定并关闭</el-button>
                  <el-button type="primary" @click="clickSure" size="small" style="margin-right: 10px">确定</el-button>
                  <el-button size="small" @click="cancel" style="margin-right: 500px">取消</el-button>
                </el-col>
              </el-row>
            </el-form>
          </div>
        </el-collapse-transition>
  
        <!-- 数据表格 -->
        <VmBaseTable
          :setTableHigh="true"
          ref="score_table"
          :data="dataTable"
          :columns="dataColumns"
          @page-change="pageChange"
          @on-select-change="selectChange"
          showCheck
          :tableHigh="tableHigh"
          @selection-change="selectChange"
        >
          <!-- 定义操作列的插槽 -->
          <template #operation="{ row }">
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"   
            >删除</el-button>
          </template>
        </VmBaseTable>
      </el-card>
  
      <!-- 隐藏的文件输入元素用于成绩录入 -->
      <input
        ref="fileInput"
        type="file"
        accept=".xls,.xlsx"
        style="display: none;"
        @change="handleFileUpload"
        multiple
      />
    </div>
  </template>
  
  <script>
    import axios from 'axios'; // 引入 Axios 进行 HTTP 请求
    import VmBaseTable from '../base/base-table.vue';
  
    export default {
      name: "score",
      components: {
        VmBaseTable
      },
      data() {
        return {
          loading: false,
          courseArr: ['数据结构', '操作系统', '数据库系统'],
          classArr: ['计算机科学 2021', '计算机科学 2022', '软件工程 2021'],
          professionArr: ['计算机科学', '软件工程', '信息技术'],
          gradeArr: ['计算机科学 2021', '计算机科学 2022', '软件工程 2021'],
          professionObj: {},
          batch: false,
          showInput: '',
          show: false,
          form: {
            profession: '',
            grade: '',
            term: '',
            courseName: '',
            year: '',
            student_name: '',
            major: '',
          },
          yearArr: [
            { label: '2021', value: 2021 },
            { label: '2022', value: 2022 },
            { label: '2023', value: 2023 }
          ],
          termArr: [
            { label: '上学期', value: 1 },
            { label: '下学期', value: 2 }
          ],
          searchValue: {
            $limit: 10,
            $offset: 0,
          },
          selection: [], // 存储选中的记录
          dataTable: [],  // 表格数据初始化为空
          baseColumns: [
            { label: '学生姓名', prop: 'student_name', style: 'center', minWidth: '100' },
            { label: '专业', prop: 'major', style: 'center', minWidth: '100' },
          ],
          categoryColumnsMap: {
            '春季必修学分': { label: '春季必修学分', prop: 'spring_required_credits', style: 'center', minWidth: '130' },
            '秋季必修学分': { label: '秋季必修学分', prop: 'autumn_required_credits', style: 'center', minWidth: '130' },
            '春季核心课程学分': { label: '春季核心课程学分', prop: 'spring_core_credits', style: 'center', minWidth: '150' },
            '秋季核心课程学分': { label: '秋季核心课程学分', prop: 'autumn_core_credits', style: 'center', minWidth: '150' },
            '数字逻辑学分': { label: '数字逻辑学分', prop: 'numerical_logic_credits', style: 'center', minWidth: '120' },
            '春季限选学分': { label: '春季限选学分', prop: 'spring_limited_credits', style: 'center', minWidth: '130' },
            '秋季限选学分': { label: '秋季限选学分', prop: 'autumn_limited_credits', style: 'center', minWidth: '130' },
            '企业实训/专业实践': { label: '企业实训/专业实践', prop: 'short_term_training_credits', style: 'center', minWidth: '200' },
            '国际化课程学分': { label: '国际化课程学分', prop: 'international_credits', style: 'center', minWidth: '150' },
            '专业选修学分': { label: '专业选修学分', prop: 'elective_credits', style: 'center', minWidth: '130' },
            '外专业学分': { label: '外专业学分', prop: 'outmajor_credits', style: 'center', minWidth: '120' },
            '素质核心学分': { label: '素质核心学分', prop: 'culture_core_credits', style: 'center', minWidth: '130' },
            '素质选修学分': { label: '素质选修学分', prop: 'culture_choose_credits', style: 'center', minWidth: '130' },
            '创新创业学分': { label: '创新创业学分', prop: 'innovation_credits', style: 'center', minWidth: '130' },
          },
          // 始终包含删除操作列
          operationColumn: {
            label: '操作',
            prop: 'operation',
            style: 'center',
            minWidth: '100',
            slot: 'operation',
          },
          dataColumns: [],  // 用于显示的表格列
        };
      },
      methods: {
        selectChange(selection) {
          this.selection = selection;
        },
        getDefault() {
          this.form.year = 2023;
          let month = new Date().getMonth() + 1;
          this.form.term = month > 2 && month < 6 ? this.termArr[0].value : this.termArr[1].value;
          // 始终显示所有列，包括操作列
          this.dataColumns = [...this.baseColumns, ...Object.values(this.categoryColumnsMap), this.operationColumn];
          this.fetchData(this.searchValue);
        },
        cancel() {
          this.form = { profession: '', grade: '', term: '', courseName: '' };
          this.show = !this.show;
        },
        change() {
          this.show = !this.show;
        },
        clickSure() {
          this.searchValue.$offset = 0;
          if (this.$refs['score_table']) this.$refs['score_table'].currentPageToOne();
          this.fetchData(this.searchValue);
        },
        clickAndClose() {
          this.clickSure();
          this.show = !this.show;
        },
        professionChange(data) {
          this.form.grade = '';
          this.form.courseName = '';
          this.form.profession = data.profession;
        },
        fetchData(page) {
          this.loading = true;
          axios.get('http://127.0.0.1:5000/data', { params: { ...page, ...this.form } })
            .then(response => {
              this.dataTable = response.data;
              this.loading = false;
            })
            .catch(error => {
              this.$message.error('获取数据失败');
              this.loading = false;
            });
        },
        pageChange(page) {
          this.searchValue.$limit = page.limit;
          this.searchValue.$offset = page.offset;
          this.fetchData(this.searchValue);
        },
        exportMethod() {
          axios.get('http://127.0.0.1:5000/data', { params: { ...this.form } })
            .then(response => {
              const list = response.data;
              this.exportExcel(list, "学生成绩列表");
            })
            .catch(() => {
              this.$message.error('导出失败');
            });
        },
        exportExcel(list, title) {
          require.ensure([], () => {
            const { export_json_to_excel } = require('../vendor/Export2Excel');
            const tHeader = this.dataColumns.map(col => col.label);
            const data = list.map(item => this.dataColumns.map(col => item[col.prop]));
            export_json_to_excel(tHeader, data, title);
          });
        },
        handleDelete(row) {
          this.$confirm('此操作将永久删除该记录, 是否继续?', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {
            axios.post('http://127.0.0.1:5000/delete', {
              student_name: row.student_name,
              major: row.major
            })
            .then(() => {
              this.$message.success('删除成功');
              this.fetchData(this.searchValue);
            })
            .catch(() => {
              this.$message.error('删除失败');
            });
          });
        },
        batchDelete() {
          this.$confirm('此操作将永久删除选中的记录, 是否继续?', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {
            const records = this.selection.map(row => ({
              student_name: row.student_name,
              major: row.major
            }));
            axios.post('http://127.0.0.1:5000/delete_batch', { records })
              .then(() => {
                this.$message.success('批量删除成功');
                this.fetchData(this.searchValue);
              })
              .catch(() => {
                this.$message.error('批量删除失败');
              });
          });
        },
        addEntry() {
          this.$refs.fileInput.click(); // 打开文件选择框
        },

         handleFileUpload(event) {
            const files = event.target.files;
            if (files.length === 0) {
                this.$message.warning('请选择要上传的文件');
                return;
            }

            // 创建 FormData 对象
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append('file', files[i]);  // 将多个文件添加到 formData
            }

            // 将学生姓名和专业等额外字段也添加到 formData 中
            formData.append('student_name', this.form.student_name || '未命名学生');
            formData.append('major', this.form.major || '未命名专业');

            // 发送文件到后端
            axios.post('http://127.0.0.1:5000/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            })
            .then(response => {
                this.$message.success('文件上传成功');
                // 上传成功后可以刷新数据或进行其他操作
                this.fetchData(this.searchValue);
            })
            .catch(error => {
                console.error('文件上传失败:', error);
                this.$message.error('文件上传失败');
            });
        },
      },
      watch: {
        'form.grade'(newVal) {
          if (newVal) {
            // 切换类别时，始终包含操作列
            this.dataColumns = [
              ...this.baseColumns,
              this.categoryColumnsMap[newVal],
              this.operationColumn
            ];
          } else {
            // 显示所有类别列和操作列
            this.dataColumns = [...this.baseColumns, ...Object.values(this.categoryColumnsMap), this.operationColumn];
          }
          this.fetchData(this.searchValue);
        }
      },
      mounted() {
        this.getDefault();
      },
      computed: {
        tableHigh() {
          return this.show ? '66vh' : '75vh';
        },
        categoryOptions() {
          return Object.keys(this.categoryColumnsMap);
        }
      }
    };
  </script>
  
  <style scoped>
    .cardStyle {
      height: 78vh;
      margin: 10px;
      padding: 15px 10px 10px 10px;
    }
  </style>
  