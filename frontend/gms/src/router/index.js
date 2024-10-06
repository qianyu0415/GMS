import { createRouter, createWebHistory } from 'vue-router';
import DataTable from '../components/DataTable.vue';
import Score from '../components/Score.vue';
import home from '../components/home.vue';

// 定义路由规则
const routes = [
  {
    path: '/home',
    name: 'home',
    component: home,
    redirect: '/score',
    children:[
      {
        path: '/score',
        name: '成绩',
        component: Score
      }
    ]
  }
  
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(), // 使用 history 模式
  routes
});

export default router;
