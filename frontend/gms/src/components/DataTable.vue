<template>
  <van-table :columns="columns" :data="tableData" />
</template>

<script>
export default {
  props: {
    tableData: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      columns: [
        { title: '序号', key: 'id' },
        { title: '学号', key: 'studentId' },
        { title: '姓名', key: 'name' },
        { title: '专业', key: 'major' },
        { title: '必修课(春)', key: 'springRequired' },
        { title: '必修课(秋)', key: 'autumnRequired' },
        { title: '核心课(春)', key: 'springCore' },
        { title: '核心课(秋)', key: 'autumnCore' },
        { title: '数字逻辑', key: 'numericalLogic' },
        { title: '限选课(春)', key: 'springLimited' },
        { title: '限选课(秋)', key: 'autumnLimited' },
        { title: '企业短期实训', key: 'shortTermTraining' },
        { title: '国际化课程', key: 'internationalCurriculum' },
        { title: '专业选修课', key: 'majorChoosed' },
        { title: '外专业学分', key: 'outMajorCredits' },
        { title: '素质核心', key: 'cultureCore' },
        { title: '素质选修', key: 'cultureChoose' },
        { title: '创新创业', key: 'innovation' }
      ]
    };
  }
};
</script>

<style scoped>
/* 可以根据需求调整表格的样式 */
</style>
