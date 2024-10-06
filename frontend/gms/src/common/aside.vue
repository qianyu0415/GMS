<template>
  <div>
    <el-menu
      :collapse="collapse"
      class="aside"
      router
    >
      <el-menu-item index="dashboard" :class="{active: $route.name === '主页'}">
        <i class="el-icon-s-home"></i>
        <span slot="title">&#12288主页</span>
      </el-menu-item>

      <el-menu-item index="timetable" :class="{active: $route.name === '课程表'}">
        <i class="el-icon-s-grid"></i> &#12288课程表
      </el-menu-item>

      <el-menu-item index="score" :class="{active: $route.name === '成绩查询'}">
        <i class="el-icon-s-unfold"></i>
        <span slot="title">&#12288成绩查询</span>
      </el-menu-item>

      <el-menu-item index="analysis" :class="{active: $route.name === '成绩详情'}">
        <i class="el-icon-s-data"></i>
        <span slot="title">&#12288成绩详情</span>
      </el-menu-item>

      <!-- 删除与 level 相关的菜单项 -->
    </el-menu>
  </div>
</template>

<script>
  export default {
    name: "Aside",
    data () {
      return {
        collapse: false,
      }
    },
    methods: {
      isCollapse () {
        this.collapse = !this.collapse;
        this.$emit('collapse', this.collapse);
      }
    }
  }
</script>
<style scoped>
  .el-submenu .el-menu-item {
    margin-left: 61px;
  }
    /*子导航栏时的样式*/
  /deep/ .el-submenu .el-menu-item {
    min-width: 80px !important;
    width: 164px;
    height: 40px;
    margin-bottom: 5px !important;
    margin-left: 40px !important;
    line-height: 40px;
    text-align: center;
    border-radius: 55px;
  }
  /*/deep/ .el-menu-item.is-active {*/
    /*background-color: #409EFF;*/
    /*color: white;*/
  /*}*/
  /deep/ .el-menu-item-group__title {
    padding: 0;
  }
  .el-menu {
    border: 0;
    /*background-image: linear-gradient(#4777e7, rgba(90,139,255,0.68));*/
  }

  .active {
    background-color: #409EFF;
    color: white;
  }
</style>
