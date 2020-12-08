<template>

  <div class="app-container">

    <el-dialog :visible.sync="centerDialogVisible" title="添加" width="45%" >
      <el-form label-width="70px">
        <el-form-item label="网卡名称">
          <el-input v-model="networkInfo.net_work_name"></el-input>
        </el-form-item>
        <el-form-item label="子网">
          <el-input v-model="networkInfo.net_work_subnet"></el-input>
        </el-form-item>
        <el-form-item label="网关">
          <el-input v-model="networkInfo.net_work_gateway"></el-input>
        </el-form-item>
        <el-form-item label="范围">
          <el-select v-model="networkInfo.net_work_scope" placeholder="请选择活动区域">
            <el-option label="local" value="local"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="驱动">
          <el-select v-model="networkInfo.net_work_driver" placeholder="请选择活动区域">
            <el-option label="bridge" value="bridge"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="IPv6">
          <el-switch v-model="networkInfo.enable_ipv6"></el-switch>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleCreate()">提 交</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
    <div class="filter-container">
      <el-input v-model="search" style="width: 230px;" size="medium"></el-input>
      <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-search" @click="handleQuery">
        查询
      </el-button>
      <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-edit" @click="openCreate">
        添加
      </el-button>
    </div>
    <el-table :data="tableData" border stripe style="width: 100%">
      <el-table-column type="index" width="50"></el-table-column>
      <el-table-column prop="net_work_name" label="网卡名称" width="180"></el-table-column>
      <el-table-column prop="net_work_subnet" label="子网" width="180"></el-table-column>
      <el-table-column prop="net_work_gateway" label="网关"></el-table-column>
      <el-table-column label="范围">
        <template slot-scope="{row}">
          <el-tag>{{row.net_work_scope}}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="驱动">
        <template slot-scope="{row}">
          <el-tag>{{row.net_work_driver}}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="启用IPv6">
        <template slot-scope="{row}">
          <el-tag>{{row.enable_ipv6}}</el-tag>
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作">
        <template slot-scope="{row}">
          <el-button size="mini" type="danger" icon="el-icon-delete" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div style="margin-top: 20px">
      <el-pagination
        :page-size="page.size"
        @current-change="netWorkList"
        layout="total, prev, pager, next, jumper"
        :total="page.total">
      </el-pagination>
    </div>
  </div>
</template>

<script>
import { NetWorkList,NetWorkAdd,NetworkDelete } from '@/api/network'
import Message from 'element-ui/packages/message/src/main'

export default {
  name: 'index',
  data() {
    return {
      tableData: [],
      search: "",
      page:{
        total: 0,
        size: 20,
      },
      centerDialogVisible: false,
      networkInfo: {
        net_work_name: "",
        net_work_subnet: "",
        net_work_gateway: "",
        net_work_scope: "local",
        net_work_driver: "bridge",
        enable_ipv6: false,
      }
    }
  },
  created(){
    this.netWorkList(1)
  },
  methods:{
    netWorkList(page){
      let search = this.search
      NetWorkList(search, page).then(response => {
        let data = response.data.results
        this.tableData = data
        this.page.total = response.data.count
      })
    },
    openCreate(){
      this.centerDialogVisible = true
    },
    handleCreate(){
      NetWorkAdd(this.networkInfo).then(response => {
        let rsDta = response.data
        if (rsDta.status === 200){
          this.$message({
            type: 'success',
            message: '添加成功!'
          })
          this.netWorkList()
          this.centerDialogVisible = false
        }else{
          Message({
            message: rsDta.msg,
            type: 'error',
            showClose: false,
            duration: 3 * 1000
          })
        }
      })
    },
    handleDelete(row){
      this.$confirm('确认删除?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        NetworkDelete(row.net_work_id).then(response => {
          let data = response.data
          if(data.status === 200){
            this.$message({
              type: 'success',
              message: '删除成功!'
            })
            this.netWorkList()
          }else{
            this.$message({
              type: 'error',
              message: data.msg
            });
          }
        })
      }).catch(() => {
      });
    },
    handleQuery(){
      this.netWorkList(1)
      // NetWorkList(this.search).then(response => {
      //   this.tableData = response.data
      // })
    }
  }
}
</script>

<style scoped>

</style>
