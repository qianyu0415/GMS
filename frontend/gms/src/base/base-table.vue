<template>
    <div>
      <el-row>
        <el-col :span="24">
          <el-table
            ref="refTable"
            :data="data"
            :header-cell-style="headerStyle"
            :row-style="rowStyle"
            :cell-style="{fontSize:'14px'}"
            :highlight-current-row="rowLight"
            :stripe="!stripe"
            @sort-change="sortChange"
            @selection-change="selectChange"
            @row-click="rowClick"
            style="width:100%;"
            :height="tableHigh">
            <!-- 多选框列 -->
            <el-table-column v-if="showCheck" type="selection" width="50px" align="center" :selectable="selectable">
            </el-table-column>
            <!-- 序号列 -->
            <el-table-column v-if="showIndex" type="index" label="序号" width="60" align="center">
            </el-table-column>
            <!-- 数据列 -->
            <el-table-column
              v-for="(col, index) in columns"
              :key="index"
              :min-width="col.minWidth"
              :show-overflow-tooltip="overflow"
              :prop="col.prop"
              :align="col.style"
              :type="col.type"
              :fixed="col.fixed"
              :sortable="col.sortable"
              :label="col.label">
              <!-- 判断是否有插槽 -->
              <template v-if="col.slot" v-slot="scope">
                <slot :name="col.slot" v-bind="scope"></slot>
              </template>
              <!-- 默认显示内容 -->
              <template v-else v-slot="scope">
                <span>
                  {{ scope.row[col.prop] }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-col>
      </el-row>
    </div>
  </template>
  
  <script>
  export default {
    name: "VmBaseTable",
    props: {
      headerStyle: {
        type: Object,
        default: () => ({ background: '#EDF1F4' })
      },
      rowStyle: {
        type: Object,
        default: () => ({})
      },
      stripe: {
        type: Boolean,
        default: false
      },
      selectable: {
        type: Function,
        default: () => true
      },
      data: {
        type: Array,
        default: () => []
      },
      columns: {
        type: Array,
        default: () => []
      },
      overflow: {
        type: Boolean,
        default: false
      },
      showCheck: {
        type: Boolean,
        default: false
      },
      showIndex: {
        type: Boolean,
        default: false
      },
      setTableHigh: {
        type: Boolean,
        default: false
      },
      tableHigh: {
        type: String,
        default: '70vh'
      },
      rowLight: {
        type: Boolean,
        default: false
      }
    },
    data() {
      return {
        selectionArr: []
      };
    },
    methods: {
      rowClick(row, column, event) {
        this.$emit('on-row-click', { row, column, event });
      },
      selectChange(selection) {
        this.selectionArr = selection;
        this.$emit('on-select-change', selection);
      },
      sortChange({ column, prop, order }) {
        this.$emit('sort-change', column, prop, order);
      },
      toggleSelection(rows) {
        if (rows) {
          rows.forEach(row => {
            this.$refs.refTable.toggleRowSelection(row);
          });
        } else {
          this.$refs.refTable.clearSelection();
        }
      },
      resize(h) {
        if (this.$refs.refTable) {
          this.$refs.refTable.height = h;
        }
      },
      getSelection(row, selected) {
        this.$refs.refTable.toggleRowSelection(row, selected);
      }
    },
    mounted() {
      this.$nextTick(() => {
        if (this.$refs.refTable) {
          this.$refs.refTable.doLayout();
        }
      });
    },
    watch: {
      data() {
        if (this.$refs.refTable && this.$refs.refTable.$el) {
          this.$refs.refTable.$el.style.width = '99.99%';
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .el-table {
    border-top: 1px solid #E7E7E7;
    border-right: 1px solid #E7E7E7;
    border-radius: 4px;
    width: 100%;
    margin-top: 5px;
  }
  /* 穿透样式 */
  ::v-deep .el-table td {
    border-bottom: 1px solid #E7E7E7;
    border-left: 1px solid #E7E7E7;
  }
  ::v-deep .el-table th {
    border-bottom: 1px solid #E7E7E7;
    border-left: 1px solid #E7E7E7;
  }
  ::v-deep .el-table tr:hover {
    background: #d2d2d2;
  }
  .el-table__fixed-right {
    height: auto !important;
    bottom: 17px;
  }
  .el-table__fixed {
    height: auto !important;
    bottom: 17px;
  }
  .el-table th, .el-table tr {
    font-family: Serif !important;
  }
  </style>
  