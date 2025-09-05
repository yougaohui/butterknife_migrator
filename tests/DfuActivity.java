package com.onmicro.omtoolbox.dfu;
import android.app.LoaderManager;
import android.app.NotificationManager;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.Context;
import android.content.CursorLoader;
import android.content.Intent;
import android.content.Loader;
import android.database.Cursor;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.provider.MediaStore;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.MimeTypeMap;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.RadioButton;
import android.widget.RelativeLayout;
import android.widget.SeekBar;
import android.widget.TableLayout;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.widget.Toolbar;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import com.onmicro.omtoolbox.BaseActivity;
import com.onmicro.omtoolbox.R;
import com.onmicro.omtoolbox.R2;
import com.onmicro.omtoolbox.adapter.DividerItemDecoration;
import com.onmicro.omtoolbox.adapter.FileListAdapter;
import com.onmicro.omtoolbox.model.BaseReponse;
import com.onmicro.omtoolbox.model.FirmwareInfo;
import com.onmicro.omtoolbox.network.ApiHelper;
import com.onmicro.omtoolbox.network.MyObserver;
import com.onmicro.omtoolbox.network.ObserverOnNextListener;
import com.onmicro.omtoolbox.scanner.ExtendedBluetoothDevice;
import com.onmicro.omtoolbox.scanner.ScannerFragment;
import com.onmicro.omtoolbox.util.AppUtils;
import com.onmicro.omtoolbox.util.CloseUtils;
import com.onmicro.omtoolbox.util.LogUtils;
import com.onmicro.omtoolbox.util.SDCardUtils;
import com.onmicro.omtoolbox.util.SPUtils;
import com.onmicro.omtoolbox.util.ToastUtils;
import com.onmicro.omtoolbox.widget.dialog.CustomPopWindow;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.List;
import java.util.Locale;
import no.nordicsemi.android.dfu.DfuProgressListener;
import no.nordicsemi.android.dfu.DfuProgressListenerAdapter;
import no.nordicsemi.android.dfu.DfuServiceInitiator;
import no.nordicsemi.android.dfu.DfuServiceListenerHelper;
public class DfuActivity extends BaseActivity implements CompoundButton.OnCheckedChangeListener,
        ScannerFragment.OnDeviceSelectedListener, LoaderManager.LoaderCallbacks<Cursor> {
    private static final String TAG = "DfuActivity";
    private static final String EXTRA_URI = "uri";
    private static final int ENABLE_BT_REQ = 0;
    private static final int SELECT_FILE_REQ = 1;
    private static final int DFU_FROM_NET = 0;
    private static final int DFU_FROM_LOCAL = 1;
    Toolbar toolbar;
    TextView tv_device_name;
    TextView tv_device_address;
    RadioButton rb_net;
    RelativeLayout rl_chip_model;
    EditText et_chip_model;
    Button btn_sure;
    RelativeLayout rl_dfu_file;
    TextView tv_dfu_file_name;
    ImageView iv_file_expload;
    TextView tv_update_desc;
    RadioButton rb_local;
    TableLayout tl_file;
    TextView tv_file_name;
    TextView tv_file_size;
    TextView tv_file_status;
    Button btn_select_file;
    Button btn_update;
    private BluetoothDevice selectedDevice;
    private String filePath;
    private Uri fileStreamUri;
    private boolean statusOk;
    private boolean isNetDownload;
    private boolean isFilterName;
    private String filterName;
    private boolean isFilterRssi;
    private int filterRssi = -60;
    private int dfuFrom = DFU_FROM_LOCAL;
    private String chipModel = "6621D";
    private List<FirmwareInfo> firmwareInfos;
    private FirmwareInfo selectFirmwareInfo;
    private DownloadOtaTask downloadOtaTask;
    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_dfu);
        isFilterName = SPUtils.getBoolean(this, SPUtils.IS_FILTER_NAME, isFilterName);
        filterName = SPUtils.getString(this, SPUtils.FILTER_NAME);
        isFilterRssi = SPUtils.getBoolean(this, SPUtils.IS_FILTER_RSSI, isFilterRssi);
        filterRssi = SPUtils.getInt(this, SPUtils.FILTER_RSSI, filterRssi);
        dfuFrom = SPUtils.getInt(this, SPUtils.DFU_UPDATE_METHOD, dfuFrom);
        rb_net.setOnCheckedChangeListener(this);
        rb_local.setOnCheckedChangeListener(this);
        isNetDownload = (dfuFrom == DFU_FROM_LOCAL);
        if (dfuFrom != DFU_FROM_LOCAL) {
            rb_net.setChecked(true);
        } else {
            rb_local.setChecked(true);
        }
        DfuServiceListenerHelper.registerProgressListener(this, dfuProgressListener);
        String jsonString = SPUtils.getString(this, SPUtils.FIRMWARE_INFO_JSON);
        if (!TextUtils.isEmpty(jsonString)) {
            try {
                selectFirmwareInfo = new Gson().fromJson(jsonString, new TypeToken<FirmwareInfo>() {}.getType());
                if (selectFirmwareInfo != null) {
                    tv_dfu_file_name.setText(String.format(Locale.ROOT, "%s_%s_%s_V%d", selectFirmwareInfo.getChip_model(),
                            selectFirmwareInfo.getProject_name(), selectFirmwareInfo.getProject_number(), selectFirmwareInfo.getFirmware_version()));
                    tv_update_desc.setText(selectFirmwareInfo.getUpdate_desc());
                }
            } catch (Exception e) {
                LogUtils.e(TAG, e.getMessage());
            }
        }
        chipModel = SPUtils.getString(this, SPUtils.CHIP_MODEL, chipModel);
        et_chip_model.setText(chipModel);
        if (!TextUtils.isEmpty(chipModel)) {
            et_chip_model.setSelection(chipModel.length());
            request_firmware_infos(chipModel);
        }
        et_chip_model.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {
            }
            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
            }
            @Override
            public void afterTextChanged(Editable s) {
                if (selectFirmwareInfo != null) {
                    selectFirmwareInfo = null;
                }
            }
        });
    
        initViews();
        initListener();}
    @Override
    public void initTopBar() {
        super.initTopBar();
        setSupportActionBar(toolbar);
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
    }
    private boolean isBLEEnabled() {
        final BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
        return adapter != null && adapter.isEnabled();
    }
    private void showBLEDialog() {
        final Intent enableIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
        startActivityForResult(enableIntent, ENABLE_BT_REQ);
    }
    private void showDeviceScanningDialog() {
        final ScannerFragment dialog = ScannerFragment.getInstance();
        dialog.show(getSupportFragmentManager(), "scan_fragment");
    }
    private void showFliterDialog() {
        View view = LayoutInflater.from(DfuActivity.this).inflate(R.layout.dialog_fliter_settings, null);
        CheckBox cb_name = view.findViewById(R.id.cb_name);
        EditText et_name = view.findViewById(R.id.et_name);
        CheckBox cb_rssi = view.findViewById(R.id.cb_rssi);
        SeekBar seekBar = view.findViewById(R.id.seekBar);
        TextView tv_rssi = view.findViewById(R.id.tv_rssi);
        cb_name.setChecked(isFilterName);
        et_name.setText(filterName);
        cb_rssi.setChecked(isFilterRssi);
        tv_rssi.setText(String.format(Locale.ROOT, "%ddBm", filterRssi));
        seekBar.setProgress(Math.abs(filterRssi));
        seekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                tv_rssi.setText(String.format(Locale.ROOT, "%ddBm", progress * (-1)));
            }
            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {
            }
            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {
            }
        });
        new AlertDialog.Builder(DfuActivity.this)
                .setView(view)
                .setNegativeButton(R.string.cancel, null)
                .setPositiveButton(R.string.sure, (dialog, which) -> {
                    isFilterName = cb_name.isChecked();
                    isFilterRssi = cb_rssi.isChecked();
                    filterName = et_name.getText().toString().trim();
                    filterRssi = seekBar.getProgress() * (-1);
                    SPUtils.putBoolean(DfuActivity.this, SPUtils.IS_FILTER_NAME, isFilterName);
                    SPUtils.putBoolean(DfuActivity.this, SPUtils.IS_FILTER_RSSI, isFilterRssi);
                    SPUtils.putString(DfuActivity.this, SPUtils.FILTER_NAME, filterName);
                    SPUtils.putInt(DfuActivity.this, SPUtils.FILTER_RSSI, filterRssi);
                })
                .show();
    }
    @Override
    public boolean onCreateOptionsMenu(final Menu menu) {
        getMenuInflater().inflate(R.menu.dfu_menu, menu);
        return true;
    }
    @Override
    public boolean onOptionsItemSelected(final MenuItem item) {
        int itemId = item.getItemId();
        if (itemId == android.R.id.home) {
            onBackPressed();
        } else if (itemId == R.id.action_scanner) {
            if (isBLEEnabled()) {
                showDeviceScanningDialog();
            } else {
                showBLEDialog();
            }
        } else if (itemId == R.id.action_scanner_fliter) {
            showFliterDialog();
        }
        return true;
    }
    
    public void onClick(View view) {
        int id = view.getId();
        if (id == R.id.btn_sure) {
            chipModel = et_chip_model.getText().toString().trim();
            if (TextUtils.isEmpty(chipModel)) {
                ToastUtils.showSingleToast(DfuActivity.this, "请输入芯片型号");
                return;
            }
            SPUtils.putString(DfuActivity.this, SPUtils.CHIP_MODEL, chipModel);
            request_firmware_infos(chipModel);
        } else if (id == R.id.iv_file_expload) {// 展开或隐藏文件列表
            if (TextUtils.isEmpty(chipModel)) {
                ToastUtils.showSingleToast(DfuActivity.this, getString(R.string.input_chip_model_tip));
                return;
            }
            showFileListPop();
        } else if (id == R.id.btn_select_file) {
            openFileChooser();
        } else if (id == R.id.btn_update) {
            if (selectedDevice == null) {
                ToastUtils.showSingleToast(DfuActivity.this, "请选择设备");
                return;
            }
//            if (getString(R.string.dfu_status_successed).equals(btn_update.getText().toString().trim())) {
//                finish();
//                return;
//            }
            if (isNetDownload) {
                if (selectFirmwareInfo == null) {
                    ToastUtils.showSingleToast(DfuActivity.this, "请选择DFU升级文件");
                    return;
                }
                // 下载固件
                if (downloadOtaTask != null && !downloadOtaTask.isCancelled()) {
                    downloadOtaTask.cancel(true);
                }
                downloadOtaTask = new DownloadOtaTask();
                downloadOtaTask.execute(selectFirmwareInfo.getUrl());
            } else {
                if (!statusOk) {
                    ToastUtils.showSingleToast(DfuActivity.this, "升级文件无效，请重新选择升级文件！");
                    return;
                }
                btn_update.setClickable(false);
                startOta();
            }
        }
    }
    private void openFileChooser() {
        final Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
        intent.setType(DfuService.MIME_TYPE_ZIP);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        if (intent.resolveActivity(getPackageManager()) != null) {
            startActivityForResult(intent, SELECT_FILE_REQ);
        } else {
            ToastUtils.showSingleToast(DfuActivity.this, "请安装文件管理器");
        }
    }
    private void updateFileInfo(final String fileName, final long fileSize) {
        tv_file_name.setText(fileName);
        tv_file_size.setText(String.format(Locale.ROOT, getString(R.string.dfu_file_size_text), fileSize));
        final String extension = "(?i)ZIP";
        statusOk = MimeTypeMap.getFileExtensionFromUrl(fileName).matches(extension);
        tv_file_status.setText(statusOk ? "OK" : getString(R.string.dfu_file_status_invalid));
    }
    private void updateUI() {
        rl_chip_model.setAlpha(isNetDownload ? 1.0f : 0.3f);
        btn_sure.setEnabled(isNetDownload);
        rl_dfu_file.setAlpha(isNetDownload ? 1.0f : 0.3f);
        tl_file.setAlpha(isNetDownload ? 0.3f : 1.0f);
        btn_select_file.setEnabled(!isNetDownload);
        if (!isNetDownload) {
            tv_update_desc.setVisibility(View.GONE);
        }
        SPUtils.putInt(DfuActivity.this, SPUtils.DFU_UPDATE_METHOD, isNetDownload ? DFU_FROM_NET : DFU_FROM_LOCAL);
    }
    private void showFileListPop() {
        View view = LayoutInflater.from(DfuActivity.this).inflate(R.layout.pop_file_list, null);
        TextView tv_empty_desc = view.findViewById(R.id.tv_empty_desc);
        if (firmwareInfos == null || firmwareInfos.isEmpty()) {
            tv_empty_desc.setVisibility(View.VISIBLE);
            tv_empty_desc.setText(String.format(Locale.ROOT, getString(R.string.no_file_tip), chipModel, chipModel));
        } else {
            tv_empty_desc.setVisibility(View.INVISIBLE);
        }
        RecyclerView recyclerView = view.findViewById(R.id.recyclerView);
        recyclerView.setHasFixedSize(true);
        recyclerView.setLayoutManager(new LinearLayoutManager(DfuActivity.this));
        recyclerView.addItemDecoration(new DividerItemDecoration(DfuActivity.this, DividerItemDecoration.VERTICAL_LIST, R.drawable.divider));
        FileListAdapter fileListAdapter = new FileListAdapter(firmwareInfos);
        recyclerView.setAdapter(fileListAdapter);
        CustomPopWindow popWindow = new CustomPopWindow.PopupWindowBuilder(DfuActivity.this)
                .setView(view)
                .setFocusable(true)
                .setOutsideTouchable(true)
                .size(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
                .setOnDissmissListener(() -> {
                    iv_file_expload.setImageResource(R.drawable.ic_arrow_down_24);
                })
                .create();
        view.findViewById(R.id.view_cancle).setOnClickListener(v -> popWindow.dissmiss());
        fileListAdapter.setOnItemClickListener(position -> {
            if (getString(R.string.dfu_status_successed).equals(btn_update.getText().toString())) {
                if (!firmwareInfos.get(position).equals(selectFirmwareInfo)) {
                    btn_update.setText("开始升级");
                }
            }
            selectFirmwareInfo = firmwareInfos.get(position);
            tv_dfu_file_name.setText(String.format(Locale.ROOT, "%s_%s_%s_V%d", selectFirmwareInfo.getChip_model(),
                    selectFirmwareInfo.getProject_name(), selectFirmwareInfo.getProject_number(), selectFirmwareInfo.getFirmware_version()));
            tv_update_desc.setText(selectFirmwareInfo.getUpdate_desc());
            String jsonString = new Gson().toJson(selectFirmwareInfo);
            SPUtils.putString(DfuActivity.this, SPUtils.FIRMWARE_INFO_JSON, jsonString);
            popWindow.dissmiss();
        });
        iv_file_expload.setImageResource(R.drawable.ic_arrow_up_24);
        popWindow.showAsDropDown(rl_dfu_file);
    }
    /**
     * 根据芯片型号请求所有的固件信息
     */
    private void request_firmware_infos(final String chipModel) {
        ApiHelper.get_firmware_infos(new MyObserver<>(new ObserverOnNextListener<BaseReponse<List<FirmwareInfo>>>() {
            @Override
            public void onNext(BaseReponse<List<FirmwareInfo>> baseReponse) {
                if (baseReponse != null) {
                    LogUtils.i(TAG, "baseReponse:" + baseReponse.toString());
                    if (baseReponse.getCode() == 200) {
                        firmwareInfos = baseReponse.getData();
                        if (firmwareInfos != null && !firmwareInfos.isEmpty()) {
                            ToastUtils.showSingleToast(DfuActivity.this, "升级文件列表请求成功");
                            if (selectFirmwareInfo == null) {
                                selectFirmwareInfo = firmwareInfos.get(0);
                                tv_dfu_file_name.setText(String.format(Locale.ROOT, "%s_%s_%s_V%d", selectFirmwareInfo.getChip_model(),
                                        selectFirmwareInfo.getProject_name(), selectFirmwareInfo.getProject_number(), selectFirmwareInfo.getFirmware_version()));
                                tv_update_desc.setText(selectFirmwareInfo.getUpdate_desc());
                            }
                        } else {
                            tv_dfu_file_name.setText(null);
                            tv_update_desc.setText(null);
                        }
                    }
                }
            }
            @Override
            public void onError(Throwable e) {
                LogUtils.e(TAG, "onError:" + e.getMessage());
                runOnUiThread(() -> {
                    ToastUtils.showSingleToast(DfuActivity.this, getString(R.string.network_no_available));
                });
            }
        }), chipModel);
    }
    /**
     * 请求服务器上的固件信息
     */
    private void request_firmware_info(final String projectName, final String projectNumber) {
        ApiHelper.get_firmware_info(new MyObserver<>(new ObserverOnNextListener<BaseReponse<FirmwareInfo>>() {
            @Override
            public void onNext(BaseReponse<FirmwareInfo> baseReponse) {
                if (baseReponse != null) {
                    LogUtils.i(TAG, "baseReponse:" + baseReponse.toString());
                    if (baseReponse.getCode() == 200) {
                        // 请求成功
                        FirmwareInfo firmwareInfo = baseReponse.getData();
                        if (firmwareInfo != null) {
                            String url = firmwareInfo.getUrl();
                            String update_desc = firmwareInfo.getUpdate_desc();
                            if (!TextUtils.isEmpty(update_desc)) {
                                if (View.VISIBLE != tv_update_desc.getVisibility()) {
                                    tv_update_desc.setVisibility(View.VISIBLE);
                                }
                                tv_update_desc.setText(update_desc);
                            } else {
                                if (View.VISIBLE == tv_update_desc.getVisibility()) {
                                    tv_update_desc.setText(View.GONE);
                                }
                            }
                            if (downloadOtaTask != null && !downloadOtaTask.isCancelled()) {
                                downloadOtaTask.cancel(true);
                            }
                            downloadOtaTask = new DownloadOtaTask();
                            downloadOtaTask.execute(url);
                            return;
                        }
                    }
                    ToastUtils.showSingleToast(DfuActivity.this, baseReponse.getMsg());
                }
                btn_update.setClickable(true);
            }
            @Override
            public void onError(Throwable e) {
                LogUtils.e(TAG, "onError:" + e.getMessage());
                runOnUiThread(() -> {
                    ToastUtils.showSingleToast(DfuActivity.this, getString(R.string.network_no_available));
                    btn_update.setClickable(true);
                });
            }
        }), 0, projectName, projectNumber);
    }
    @Override
    public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
        int id = buttonView.getId();
        if (id == R.id.rb_net) {
            if (isNetDownload != isChecked) {
                isNetDownload = isChecked;
                rb_local.setChecked(!isNetDownload);
                updateUI();
            }
        } else if (id == R.id.rb_local) {
            if (isNetDownload == isChecked) {
                isNetDownload = !isChecked;
                rb_net.setChecked(isNetDownload);
                updateUI();
            }
        }
    }
    @Override
    protected void onDestroy() {
        if (downloadOtaTask != null && !downloadOtaTask.isCancelled()) {
            downloadOtaTask.cancel(true);
        }
        super.onDestroy();
    }
    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == SELECT_FILE_REQ && resultCode == RESULT_OK) {
            filePath = null;
            fileStreamUri = null;
            if (data == null) {
                return;
            }
            final Uri uri = data.getData();
            LogUtils.i(TAG, "uri:" + uri.getScheme());
            if (uri.getScheme().equals("file")) {
                final String path = uri.getPath();
                final File file = new File(path);
                filePath = path;
                updateFileInfo(file.getName(), file.length());
            } else if (uri.getScheme().equals("content")) {
                fileStreamUri = uri;
                final Bundle extras = data.getExtras();
                if (extras != null && extras.containsKey(Intent.EXTRA_STREAM)) {
                    fileStreamUri = extras.getParcelable(Intent.EXTRA_STREAM);
                }
                // file name and size must be obtained from Content Provider
                final Bundle bundle = new Bundle();
                bundle.putParcelable(EXTRA_URI, uri);
                getLoaderManager().restartLoader(SELECT_FILE_REQ, bundle, this);
            }
        }
    }
    @Override
    public void onDeviceSelected(@NonNull ExtendedBluetoothDevice extendedBluetoothDevice) {
        if (getString(R.string.dfu_status_successed).equals(btn_update.getText().toString())) {
            if (!extendedBluetoothDevice.device.getAddress().equals(selectedDevice.getAddress())) {
                btn_update.setText("开始升级");
            }
        }
        selectedDevice = extendedBluetoothDevice.device;
        String name = selectedDevice.getName();
        tv_device_name.setText(!TextUtils.isEmpty(name) ? name : "UNKNOW");
        tv_device_address.setText(selectedDevice.getAddress());
    }
    @Override
    public void onDialogCanceled() {
    }
    @Override
    public Loader<Cursor> onCreateLoader(int id, Bundle args) {
        final Uri uri = args.getParcelable(EXTRA_URI);
        return new CursorLoader(this, uri, null, null, null, null);
    }
    @Override
    public void onLoadFinished(Loader<Cursor> loader, Cursor data) {
        if (data != null && data.moveToNext()) {
            final String fileName = data.getString(data.getColumnIndex(MediaStore.MediaColumns.DISPLAY_NAME));
            final int fileSize = data.getInt(data.getColumnIndex(MediaStore.MediaColumns.SIZE));
            String filePath = null;
            final int dataIndex = data.getColumnIndex(MediaStore.MediaColumns.DATA);
            if (dataIndex != -1) {
                filePath = data.getString(dataIndex);
            }
            if (!TextUtils.isEmpty(filePath)) {
                this.filePath = filePath;
            }
            updateFileInfo(fileName, fileSize);
        } else {
            tv_file_name.setText(null);
            tv_file_size.setText(null);
            tv_file_status.setText("文件读取失败");
            filePath = null;
            fileStreamUri = null;
            statusOk = false;
        }
    }
    @Override
    public void onLoaderReset(Loader<Cursor> loader) {
        tv_file_status.setText(null);
        tv_file_size.setText(null);
        filePath = null;
        fileStreamUri = null;
        statusOk = false;
    }
    public class DownloadOtaTask extends AsyncTask<String, Integer, Void> {
        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            btn_update.setClickable(false);
            btn_update.setText(getString(R.string.downloading));
        }
        @Override
        protected Void doInBackground(String... params) {
            InputStream is = null;
            FileOutputStream fos = null;
            try {
                URL url = new URL(params[0]);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestProperty("Accept-Encoding", "identity");
                conn.setRequestMethod("GET");
                conn.connect();
                int responseCode = conn.getResponseCode();
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    String download_path = SDCardUtils.getSDCradCacheDir(DfuActivity.this, "download_ota");
                    File download_dir = new File(download_path);
                    if (!download_dir.exists()) {
                        download_dir.mkdir();
                    }
                    File otaFile = new File(download_dir, "ota.zip");
                    filePath = otaFile.getPath();
                    if (otaFile.exists()) {
                        otaFile.delete();
                    }
                    int length = conn.getContentLength();
                    is = conn.getInputStream();
                    fos = new FileOutputStream(otaFile);
                    int readTotalCount = 0;
                    int len = 0;
                    byte[] buffer = new byte[1024];
                    while ((len = is.read(buffer, 0, 1024)) != -1) {
                        fos.write(buffer, 0, len);
                        readTotalCount += len;
                        int progress = readTotalCount * 100 / length;
                        publishProgress(progress);
                    }
                }
                conn.disconnect();
            } catch (Exception e) {
                e.printStackTrace();
            } finally {
                CloseUtils.closeIO(is);
                CloseUtils.closeIO(fos);
            }
            return null;
        }
        @Override
        protected void onProgressUpdate(Integer... values) {
            super.onProgressUpdate(values);
            if (values.length > 0) {
                int downloadProgress = values[0];
                btn_update.setText(String.format(Locale.ROOT, getString(R.string.downloading_d), downloadProgress));
                if (downloadProgress == 100) {
                    startOta();
                }
            }
        }
    }
    private boolean isDfuServiceRunning() {
        return AppUtils.isServiceRunning(this, DfuService.class.getName());
    }
    private void startOta() {
        if (isDfuServiceRunning()) {
            return;
        }
        btn_update.setText(getString(R.string.updating));
        final DfuServiceInitiator starter = new DfuServiceInitiator(selectedDevice.getAddress())
                .setDeviceName(selectedDevice.getName())
                .setKeepBond(false)
                .setForceDfu(false)
                .setPacketsReceiptNotificationsEnabled(Build.VERSION.SDK_INT < Build.VERSION_CODES.M)
                .setPacketsReceiptNotificationsValue(12)
                .setPrepareDataObjectDelay(400)
                .setUnsafeExperimentalButtonlessServiceInSecureDfuEnabled(true);
        starter.setZip(fileStreamUri, filePath);
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            starter.setForeground(false);
            starter.setDisableNotification(true);
        }
        starter.start(this, DfuService.class);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            DfuServiceInitiator.createDfuNotificationChannel(DfuActivity.this);
        }
    }
    private void cancelNotification() {
        new Handler().postDelayed(() -> {
            final NotificationManager manager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
            manager.cancel(DfuService.NOTIFICATION_ID);
        }, 200);
    }
    private final DfuProgressListener dfuProgressListener = new DfuProgressListenerAdapter() {
        @Override
        public void onDeviceConnecting(@NonNull final String deviceAddress) {
        }
        @Override
        public void onDfuProcessStarting(@NonNull final String deviceAddress) {
        }
        @Override
        public void onEnablingDfuMode(@NonNull final String deviceAddress) {
        }
        @Override
        public void onFirmwareValidating(@NonNull final String deviceAddress) {
        }
        @Override
        public void onDeviceDisconnecting(@NonNull final String deviceAddress) {
        }
        @Override
        public void onDfuCompleted(@NonNull final String deviceAddress) {
            btn_update.setText(R.string.dfu_status_successed);
            btn_update.setClickable(true);
            cancelNotification();
        }
        @Override
        public void onDfuAborted(@NonNull final String deviceAddress) {
            btn_update.setText(R.string.dfu_status_fialed);
            btn_update.setClickable(true);
            cancelNotification();
        }
        @Override
        public void onProgressChanged(@NonNull final String deviceAddress, final int percent,
                                      final float speed, final float avgSpeed,
                                      final int currentPart, final int partsTotal) {
            btn_update.setText(String.format(Locale.ROOT, getString(R.string.updating_d), percent));
        }
        @Override
        public void onError(@NonNull final String deviceAddress, final int error, final int errorType, final String message) {
            LogUtils.i(TAG, "onError:" + error);
            btn_update.setText(R.string.dfu_status_fialed);
            btn_update.setClickable(true);
            ToastUtils.showSingleToast(DfuActivity.this, "升级失败：" + message);
            cancelNotification();
        }
    };

    protected void initViews() {
        // 初始化View绑定 - 替换@BindView注解
        toolbar = findViewById(R2.id.toolbar);
        tv_device_name = findViewById(R2.id.tv_device_name);
        tv_device_address = findViewById(R2.id.tv_device_address);
        rb_net = findViewById(R2.id.rb_net);
        rl_chip_model = findViewById(R2.id.rl_chip_model);
        et_chip_model = findViewById(R2.id.et_chip_model);
        btn_sure = findViewById(R2.id.btn_sure);
        rl_dfu_file = findViewById(R2.id.rl_dfu_file);
        tv_dfu_file_name = findViewById(R2.id.tv_dfu_file_name);
        iv_file_expload = findViewById(R2.id.iv_file_expload);
        tv_update_desc = findViewById(R2.id.tv_update_desc);
        rb_local = findViewById(R2.id.rb_local);
        tl_file = findViewById(R2.id.tl_file);
        tv_file_name = findViewById(R2.id.tv_file_name);
        tv_file_size = findViewById(R2.id.tv_file_size);
        tv_file_status = findViewById(R2.id.tv_file_status);
        btn_select_file = findViewById(R2.id.btn_select_file);
        btn_update = findViewById(R2.id.btn_update);
    }

    public void initListener() {
        // 初始化点击事件 - 替换@OnClick注解
        findViewById(R2.id.btn_sure).setOnClickListener(v -> onClick(v));
        findViewById(R2.id.iv_file_expload).setOnClickListener(v -> onClick(v));
        findViewById(R2.id.btn_select_file).setOnClickListener(v -> onClick(v));
        findViewById(R2.id.btn_update).setOnClickListener(v -> onClick(v));
    }
}