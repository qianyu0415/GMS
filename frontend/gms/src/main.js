import { createApp } from 'vue';
import App from './App.vue';
import router from './router';  // 导入路由配置
import ElementPlus from 'element-plus'; // 引入 Element Plus
import 'element-plus/dist/index.css'; // 引入 Element Plus 样式
import store from './store';  // 导入 store.js 文件

// 从 Vant 中导入 Uploader 和 Button 组件
import { Uploader, Button } from 'vant'; // 引入 Vant 组件
import 'vant/lib/index.css'; // 引入 Vant 样式

// 创建 Vue 应用实例
const app = createApp(App);

// 使用 Vuex Store
app.use(store);  // 注入 store

// 使用 Vant 的 Uploader 和 Button 组件
app.use(Uploader);
app.use(Button);

// 使用 Vue Router
app.use(router);

// 使用 Element Plus
app.use(ElementPlus);

// 将 Vue 应用挂载到 HTML 中的 #app 元素
app.mount('#app');
