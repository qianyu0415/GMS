import { createStore } from 'vuex';

const store = createStore({
  state: {
    silent: false, // 初始值，可以根据你的需求设置
    collapse: {},
    userInfo: JSON.parse(localStorage.getItem('userInfo')) || null,
  },
  mutations: {
    SAVE_SILENT(state, silent) {
      state.silent = silent;
    },
    SAVE_COLLAPSE(state, collapse) {
      state.collapse = Object.assign({}, collapse);
    },
    SAVE_USERINFO(state, userInfo) {
      localStorage.setItem('userInfo', JSON.stringify(userInfo));
      state.userInfo = userInfo;
    },
  },
});

export default store;
