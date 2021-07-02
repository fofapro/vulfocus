<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="search" style="width: 230px;" size="medium"></el-input>
      <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-search" @click="handleQuery">
        查询
      </el-button>
    </div>
    <el-table :data="tableData" border stripe style="width: 100%" v-loading="loading">
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
        search: "",
        page:{
          total: 0,
          size: 20,
        },
        tableData: [],
        loading:true
      }
    },
    created() {
      this.inintTableData(1)
    },
    methods:{
      inintTableData(page){
        let search = this.search
        LogList(search, page).then(response => {
          let data = response.data.results
          this.tableData = data
          this.page.total = response.data.count
          this.loading = false
        })
      },
      handleQuery(){
        this.inintTableData(1)
      }
    }
  }
</script>

<style scoped>

</style>
