import { createApp } from 'vue';
import App from './App.vue';
import 'vant/lib/index.css'; // Vant 样式
import { Uploader, Button } from 'vant'; // 引入 Vant 组件

const app = createApp(App);

// 使用 Vant 组件
app.use(Uploader);
app.use(Button);

app.mount('#app');
