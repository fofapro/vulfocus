<template>
<div class="app-container">
  <div class="filter-container">
    <el-input v-model="search" style="width: 230px;" size="medium"></el-input>
    <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-search" @click="handleQuery">
      查询
    </el-button>
    <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-edit" @click="handleOpenCreate">
      添加
    </el-button>
  </div>
  <el-dialog :visible.sync="imageDialogVisible">
    <img width="100%" :src="dialogImageUrl" alt="">
  </el-dialog>
  <el-dialog :visible.sync="ymlDialogVisible">
    <el-input type="textarea" style="color:black;" autosize readonly v-model="dialogYml" ></el-input>
  </el-dialog>
  <el-table :data="tableData" border stripe style="width: 100%; margin-top: 20px">
    <el-table-column type="index" width="50"></el-table-column>
    <el-table-column prop="layout_name" label="环境名称" width="180"></el-table-column>
    <el-table-column prop="layout_desc" :show-overflow-tooltip=true label="环境描述" width="180"></el-table-column>
    <el-table-column label="图片" width="120px">
      <template slot-scope="{row}">
        <img @click="handleShowImage(row)" v-if="row.image_name" :src="row.image_name" style="width: 60px;height: 60px;display: block;"  alt=""/>
      </template>
    </el-table-column>
    <el-table-column
      label="日期"
      width="240">
      <template slot-scope="{row}">
        <i class="el-icon-time"></i>
        <span style="margin-left: 5px">{{ row.create_date }}</span>
      </template>
    </el-table-column>
    <el-table-column label="是否发布" width="85">
      <template slot-scope="{row}">
        <el-tag v-if="row.is_release === true">已发布</el-tag>
        <el-tag v-else-if="row.is_release === false">未发布</el-tag>
      </template>
    </el-table-column>
    <el-table-column fixed="right" label="操作">
      <template slot-scope="{row}">
        <el-button size="mini" type="primary" icon="el-icon-zoom-in" @click="handleShowYml(row)">查看</el-button>
        <el-button size="mini" type="primary" icon="el-icon-edit" @click="handleEdit(row)">修改</el-button>
        <el-button size="mini" type="primary" icon="el-icon-position" @click="handleRelease(row)" v-if="row.is_release === false">发布</el-button>
<!--        <el-button size="mini" type="primary" icon="el-icon-position" v-else-if="row.is_release === true">取消发布</el-button>-->
        <el-button size="mini" type="danger" icon="el-icon-delete" @click="handleDelete(row)">删除</el-button>
      </template>
    </el-table-column>
  </el-table>

  <div style="margin-top: 20px">
    <el-pagination
      :page-size="page.size"
      @current-change="layoutListData"
      layout="total, prev, pager, next, jumper"
      :total="page.total">
    </el-pagination>
  </div>
</div>
</template>

<script>
import {layoutList, layoutRelease, layoutDelete} from '@/api/layout'
export default {
  name: 'manager',
  data(){
    return {
      tableData: [],
      search: "",
      page:{
        total: 0,
        size: 20,
      },
      isRelease: false,
      imageDialogVisible: false,
      dialogImageUrl: "",
      ymlDialogVisible: false,
      dialogYml: ""
    }
  },
  created() {
    this.layoutListData(1)
  },
  methods:{
    layoutListData(page){
      this.tableData = []
      layoutList(this.search, page).then(response => {
        let rsp = response.data
        rsp.results.forEach((info,index) => {
          info.image_name = process.env.VUE_APP_BASE_API+ '/static/'+ info.image_name
          this.tableData.push(info)
        })
        this.page.total = rsp.count
      }).catch(err => {
        this.$message({
          type: 'error',
          message: '服务器内部错误!'
        })
      })
    },
    handleQuery(){
      this.tableData = []
      this.layoutListData(1)
    },
    handleOpenCreate(){
      this.$router.push({path:'/layout/index'})
    },
    handleDelete(row){
      this.$confirm('确认删除？删除会影响用户得分', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(()=>{
        layoutDelete(row.layout_id).then(response => {
          let rsp = response.data
          if(rsp.status === 200){
            this.$message({
              message: "删除成功",
              type: 'success'
            })
            this.layoutListData(1)
          }else{
            this.$message({
              message: rsp.msg,
              type: 'error'
            })
          }
        }).catch(err => {
          this.$message({
            message: "服务器内部错误",
            type: 'error'
          })
        })
      }).catch()
    },
    handleShowImage(row){
      this.dialogImageUrl = row.image_name
      this.imageDialogVisible = true
    },
    handleShowYml(row){
      this.dialogYml = row.yml_content
      this.ymlDialogVisible = true
    },
    handleEdit(row){
      this.$router.push({path:'/layout/index', query: {layoutId: row.layout_id, layoutData: row}})
    },
    handleRelease(row){
      layoutRelease(row.layout_id).then(response=>{
        let rsp = response.data
        let status = rsp.status
        if (status === 200){
          row.is_release = true
          this.$message({
            message: "发布成功",
            type: 'success'
          })

        }else{
          this.$message({
            message: rsp.msg,
            type: 'error'
          })
        }
      }).catch(err => {
        this.$message({
          message: "服务器内部错误",
          type: 'error'
        })
      })
    }
  }
}
</script>

<style scoped>

</style>
