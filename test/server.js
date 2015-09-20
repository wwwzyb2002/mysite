/*
server.js
*/

function getRowIndex(target) {
    var tr = $(target).closest('tr.datagrid-row');
    return parseInt(tr.attr('datagrid-row-index'));
}

function updateActions(index) {
    $('#table-servers').datagrid('updateRow',{
        index: index,
        row:{}
    });
}

function editrow(target) {
    $('#table-servers').datagrid('beginEdit', getRowIndex(target));
}

function saverow(target) {
    var index = getRowIndex(target);
    $('#table-servers').datagrid('endEdit', getRowIndex(target));

    var rows = $('#table-servers').datagrid('getRows');
    var row = rows[index];
    $.ajax("/api/qate/updateserver/", {
        type: 'POST',
        data: row,
    });
}

function cancelrow(target) {
    $('#table-servers').datagrid('cancelEdit', getRowIndex(target));
}

define([], function () {
    console.log("server.js")

    return {
        initServerInfos: function (urlStr, queryParams) {
            /* 初始化服务器表 */
            $('#table-servers').datagrid({
                title:'服务器信息列表',
                url: urlStr,
                queryParams: queryParams,
                width: 1200,
                height: 586,
                autoRowHeight: false,
                fitColumns: true,
                singleSelect: true,
                striped: true,
                pagination: true,
                pageSize: 20,
                pageNumber: 1,
                pageList: ["20"],
                rownumbers: true,
                columns: [[{
                    title: "环境",
                    field: 'env',
                    width: 80,
                    align: 'center'
                },{
                    title: "主机",
                    field: 'name',
                    width: 100,
                    align: 'center'
                }, {
                    title: "IP",
                    field: 'ip',
                    width: 120,
                    align: 'center'
                }, {
                    title: "操作系统",
                    field: 'os',
                    width: 220,
                    align: 'center'
                }, {
                    title: "CPU",
                    field: 'cpu',
                    width: 40,
                    align: 'center'
                }, {
                    title: "Memory(GB)",
                    field: 'mem',
                    width: 70,
                    align: 'center'
                }, {
                    title: "Disk(GB)",
                    field: 'disk',
                    width: 60,
                    align: 'center'
                }, {
                    title: "角色",
                    field: 'role',
                    width: 60,
                    align: 'center',
                    editor:'text'
                }, {
                    title: "PD",
                    field: 'pd',
                    width: 60,
                    align: 'center',
                    editor:'text'
                }, {
                    title: "描述",
                    field: 'desc',
                    width: 150,
                    align: 'center',
                    editor:'text'
                }, {
                    title: '操作',
                    field: 'action',
                    width: 70,
                    align: 'center',
                    formatter: function(value, row, index) {
                        if (row.editing){
                            var s = '<a href="#" onclick="saverow(this)">保存</a> ';
                            var c = '<a href="#" onclick="cancelrow(this)">取消</a>';
                            return s+c;
                        } else {
                            var e = '<a href="#" onclick="editrow(this)">编辑</a> ';
                            return e;
                        }
                    }
                }]],
                rowStyler: function(index, row) {
                    if (row.cpu == "" || row.mem == "" || row.disk == ""){
                        return 'background-color:pink;color:blue';
                    }
                },
                onBeforeEdit:function(index,row) {
                    row.editing = true;
                    updateActions(index);
                },
                onAfterEdit:function(index,row) {
                    row.editing = false;
                    updateActions(index);
                },
                onCancelEdit:function(index,row) {
                    row.editing = false;
                    updateActions(index);
                },
                onLoadSuccess: function(data) {
                    // 加载完数据后更新统计信息
                    console.log(data);
                    var info = '当前搜索条件下总CPU: ' + data.cpu_total + '(核) ';
                    info += '总内存: ' + data.mem_total + '(GB) ';
                    info += '总磁盘大小: ' + data.disk_total + '(GB)';
                    $('#p-statistics').text(info);
                }
            });
        },

        buildParams: function () {
            var env_value = $('#inp-env').combobox('getValue');
            console.log(env_value);

            var pd_value = $('#inp-pd').combobox('getValue');
            console.log(pd_value);

            var queryParams = {
                env: env_value,
                pd: pd_value,
                key: ""
            };
            return queryParams;
        },

        loadServers: function () {
            console.log("loadServers");
            var queryParams = this.buildParams();
            this.initServerInfos('/api/qate/getpageserverinfos/', queryParams);
        },

        loadEnvInfos: function () {
            console.log("loadEnvInfos");
            $('#inp-env').combobox({
                mode:'remote',
                url: '/api/qate/getenvnames/',
                method: 'get',
                valueField: 'id',
                textField: 'name',
                panelHeight: 130,
                onSelect: function(obj) {
                    console.log("onSelect inp-env");

                    /* 将搜索框置为空 */
                    $('#inp-search').searchbox('setValue', "");

                    var env_value = $('#inp-env').combobox('getValue');
                    var pd_value = $('#inp-pd').combobox('getValue');
                    $('#table-servers').datagrid({
                        queryParams: {
                            env: env_value,
                            pd: pd_value,
                            key: ""
                        }
                    });
                }
            });
            $('#inp-env').combobox('setValue', "所有环境");
        },

        loadPDInfos: function () {
            console.log("loadPDInfos");
            $('#inp-pd').combobox({
                mode:'remote',
                url: '/api/qate/getpdnames/',
                valueField: 'id',
                textField: 'name',
                onSelect: function(obj) {
                    console.log("onSelect inp-pd");
                    var env_value = $('#inp-env').combobox('getValue');
                    var pd_value = $('#inp-pd').combobox('getValue');

                    $('#inp-search').searchbox('setValue', "");
                    $('#table-servers').datagrid({
                        queryParams: {
                            env: env_value,
                            pd: pd_value,
                            key: ""
                        }
                    });
                }
            });
            $('#inp-pd').combobox('setValue', "所有PD");
        },

        initSearch: function () {
            console.log("initSearch");
            $('#inp-search').searchbox({
                searcher: function(value) {
                    $('#table-servers').datagrid({
                        queryParams: {
                            env: "所有环境",
                            pd: "所有PD",
                            key: value,
                        }
                    });
                },
                prompt:'请输入服务器名称或者IP'
            });
        }
    }
})