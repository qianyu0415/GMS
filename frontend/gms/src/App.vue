<template>
  <div id="app">
    <h1>成绩管理系统</h1>

    <!-- 文件上传组件 -->
    <div class="uploader-container">
      <van-uploader
        v-model="fileList"
        multiple
        accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel"
        @after-read="handleUpload"
        max-count="1"   
      />
    </div>

    <van-button @click="uploadFiles" type="primary">上传 Excel 文件</van-button>

    <!-- 数据表格展示组件 -->
    <DataTable :tableData="tableData" />
  </div>
</template>

<script>
import DataTable from './components/DataTable.vue';
import { Uploader, Button } from 'vant';
import axios from 'axios';

export default {
  name: 'App',
  components: {
    DataTable,  // 表格组件
    Uploader,   // 上传组件
    Button      // 按钮组件
  },
  data() {
    return {
      fileList: [],   // 存储上传的文件列表
      tableData: []   // 存储后端返回的数据
    };
  },
  methods: {
  handleUpload(file) {
    console.log('已选择文件:', file);
    this.fileList = [file];  // 将选中的文件保存到 fileList，确保每次只存储一个文件
  },
  async uploadFiles() {
    if (this.fileList.length === 0) {
      return alert("请先选择一个 Excel 文件！");
    }

    const formData = new FormData();
    this.fileList.forEach(file => {
      formData.append('file', file.file);  // 传递 file.file 确保是文件对象，而不是文件元数据
    });

    // 打印 FormData 中的内容
    for (let [key, value] of formData.entries()) {
      console.log(`${key}:`, value);
    }

    try {
      // 上传文件到后端
      const uploadResponse = await axios.post('http://127.0.0.1:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      console.log('上传成功:', uploadResponse.data);

      // 上传成功后，获取数据
      this.fetchData();
    } catch (error) {
      console.error('文件上传失败:', error.response.data);
    }
  },
//   async fetchData() {
//     try {
//       // 从后端获取处理后的数据
//       const response = await axios.get('http://127.0.0.1:5000/data');
//       console.log('获取成功的数据:', response.data);
//       this.tableData = response.data;
//     } catch (error) {
//       console.error('数据获取失败:', error);
//     }
//   }
},
  mounted() {
    this.fetchData();  // 页面加载时获取数据
  }
};
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

h1 {
  color: #42b983;
}

.uploader-container {
  margin-bottom: 20px; /* 增加一些间距，确保上传组件可见 */
}
</style>
