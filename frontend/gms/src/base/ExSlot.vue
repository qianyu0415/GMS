<template>
    <!-- 渲染函数组件，无需模板内容 -->
  </template>
  
  <script>
  import { h, defineComponent } from 'vue';
  
  export default defineComponent({
    name: 'ExSlot',
    props: {
      row: Object,
      render: Function,
      index: Number,
      column: {
        type: Object,
        default: null
      }
    },
    setup(props) {
      return () => {
        const params = {
          row: props.row,
          index: props.index,
          column: props.column
        };
        return props.render(h, params);
      };
    }
  });
  </script>
  