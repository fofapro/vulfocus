<template>
  <div class="app-container">
      <el-dialog :visible.sync="centerDialogVisible" title="环境信息" width="45%">
      <el-form label-width="80px"
               v-loading="loading"
               element-loading-text="添加中">
        <el-form-item label="漏洞名称">
          <el-input v-model="vulInfo.vul_name"></el-input>
        </el-form-item>
        <el-form-item label="镜像">
          <el-col :span="11">
            <el-upload
              v-if="imgType === 'file'"
              ref="upload"
              :http-request="uploadImg"
              accept=".tar"
              action="/CombinationImage/"
              :limit="1"
              :auto-upload="false">
              <el-button slot="trigger" size="medium" type="primary">选取文件</el-button>
            </el-upload>
            <el-input v-model="vulInfo.name" v-if="imgType === 'text'" size="medium" ></el-input>
          </el-col>
          <el-col :span="13" align="right">
            <el-button v-model="imgType" @click.stop="changeType" size="medium">{{imgTypeText}}</el-button>
          </el-col>
        </el-form-item>
        <el-form-item label="Rank">
          <el-input type="float" v-model="vulInfo.rank"></el-input>
        </el-form-item>
        <el-form-item label="描述">
          <el-input type="textarea" v-model="vulInfo.desc"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary"  @click="uploadImg">提 交</el-button>
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
    <el-table
      :data="tableData"
      border
      stripe
      align = "center"
      style="width: 100%">
      <el-table-column
        type="index"
        width="50">
      </el-table-column>
      <el-table-column
        prop="image_name"
        label="名称"
        :show-overflow-tooltip=true
        width="220">
      </el-table-column>
      <el-table-column
        prop="image_vul_name"
        label="漏洞名称"
        :show-overflow-tooltip=true
        width="180">
      </el-table-column>
      <el-table-column
        prop="image_port"
        label="端口"
        width="100">
      </el-table-column>
      <el-table-column
        prop="rank"
        label="分数"
        width="50">
      </el-table-column>
      <el-table-column
        prop="image_desc"
        :show-overflow-tooltip=true
        label="描述"
        width="360">
      </el-table-column>
      <el-table-column
        fixed="right"
        label="操作">
        <template slot-scope="{row}">
          <el-button
            size="mini"
            type="danger"
            icon="el-icon-delete"
            @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
  import { ImgList } from '@/api/docker'
  import { ImageAdd, ImageDelete } from "@/api/image"
  import Message from 'element-ui/packages/message/src/main'

  export default {
    name: 'index',
    data() {
      return {
          tableData: [],
          search: "",
          centerDialogVisible: false,
          startCon: false,
          vulInfo: {
            rank: "",
            name: "",
            vul_name: "",
            desc: "",
          },
          imgType: "file",
          imgTypeText: "切换为本",
          loading: false,
      }
    },
    created() {
      this.initTableData()
    },
    methods:{
      initTableData(){
        ImgList().then(response => {
          this.tableData = response.data
        })
      },
      openCreate(){
        this.centerDialogVisible = true
      },
      changeType(){
        if(this.imgType === 'file'){
          this.imgType = 'text'
          this.imgTypeText = "切换为文件"
        }else{
          this.imgType = 'file'
          this.imgTypeText = "切换为文本"
        }
      },
      uploadImg(fileObj) {
        let formData = new FormData()
        if (this.$refs.upload != null){
          let uploadFiles = this.$refs.upload.uploadFiles
          if (this.$refs.upload.uploadFiles != null || this.$refs.upload.uploadFiles.length > 0){
            formData.set("file", uploadFiles[0].raw);
          }
        }
        formData.set("rank", this.vulInfo.rank)
        formData.set("name", this.vulInfo.name)
        formData.set("vul_name", this.vulInfo.vul_name)
        formData.set("desc", this.vulInfo.desc)
        this.loading = true
        ImageAdd(formData).then(response => {
          this.loading = false
          let data = response.data
          if(data.status == 200){
            Message({
              message: "添加成功",
              type: 'success',
              showClose: false
            })
            this.centerDialogVisible = false
            this.initTableData()
          }else{
            Message({
              message: data.msg,
              type: 'error',
              showClose: false,
              duration: 3 * 1000
            })
            this.centerDialogVisible = false
          }
        })
      },
      handleDelete(row){
        this.$confirm('确认删除?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          ImageDelete(row.image_id).then(response => {
            let data = response.data
            if(data.status === 200){
              this.$message({
                type: 'success',
                message: '删除成功!'
              })
              this.initTableData()
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
        ImgList(this.search).then(response => {
          this.tableData = response.data
        })
      }
    }
  }
</script>

<style scoped>

</style>
