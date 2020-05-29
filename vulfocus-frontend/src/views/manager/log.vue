<template>
  <div class="app-container">
    <el-table :data="tableData" border stripe style="width: 100%">
      <el-table-column type="index" width="50"></el-table-column>
      <el-table-column prop="user_name" width="150" :show-overflow-tooltip=true label="用户名"></el-table-column>
      <el-table-column :show-overflow-tooltip=true prop="operation_type" label="操作类型" width="130"></el-table-column>
      <el-table-column :show-overflow-tooltip=true label="操作名称" width="100">
        <template slot-scope="{row}">
          <el-tag>{{row.operation_name}}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :show-overflow-tooltip=true prop="operation_value" label="操作对象"></el-table-column>
      <el-table-column :show-overflow-tooltip=true prop="operation_args" label="参数"></el-table-column>
      <el-table-column :show-overflow-tooltip=true prop="ip" label="ip"></el-table-column>
      <el-table-column :show-overflow-tooltip=true prop="create_date" label="时间"></el-table-column>
    </el-table>
    <div style="margin-top: 20px">
      <el-pagination
        :page-size="page.size"
        @current-change="inintTableData"
        layout="total, prev, pager, next, jumper"
        :total="page.total">
      </el-pagination>
    </div>
  </div>

</template>

<script>
  import {LogList} from '@/api/log'

  export default {
    name: 'log',
    data(){
      return {
        page:{
          total: 0,
          size: 20,
        },
        tableData: []
      }
    },
    created() {
      this.inintTableData(1)
    },
    methods:{
      inintTableData(page){
        LogList(page).then(response => {
          this.tableData = response.data.results
          this.page.total = response.data.count
        })
      }
    }
  }
</script>

<style scoped>

</style>
