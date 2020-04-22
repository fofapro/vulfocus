<template>
  <div class="app-container">
    <el-table
      :data="tableData"
      border
      stripe
      style="width: 100%">
      <el-table-column
        type="index"
        width="50">
      </el-table-column>
      <el-table-column
        prop="user_name"
        width="150"
        :show-overflow-tooltip=true
        label="用户名">
      </el-table-column>
      <el-table-column
        :show-overflow-tooltip=true
        prop="operation_type"
        label="操作类型">
      </el-table-column>
      <el-table-column
        :show-overflow-tooltip=true
        label="操作名称">
        <template slot-scope="{row}">
          <el-tag>{{row.operation_name}}</el-tag>
        </template>
      </el-table-column>
      <el-table-column
        :show-overflow-tooltip=true
        prop="operation_value"
        label="操作对象">
      </el-table-column>
      <el-table-column
        :show-overflow-tooltip=true
        prop="operation_args"
        label="参数">
      </el-table-column>
      <el-table-column
        :show-overflow-tooltip=true
        prop="user_name"
        label="ip">
      </el-table-column>
      <el-table-column
        :show-overflow-tooltip=true
        prop="create_date"
        label="时间">
      </el-table-column>
    </el-table>
  </div>

</template>

<script>
  import {LogList} from '@/api/log'

  export default {
    name: 'log',
    data(){
      return {
        tableData: []
      }
    },
    created() {
      this.inintTableData()
    },
    methods:{
      inintTableData(){
        LogList().then(response => {
          this.tableData = response.data
        })
      }
    }
  }
</script>

<style scoped>

</style>
